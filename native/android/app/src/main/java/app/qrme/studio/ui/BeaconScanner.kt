package app.qrme.studio.ui

import android.Manifest
import app.qrme.studio.L10n
import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.graphics.RectF
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import app.qrme.studio.ApiClient
import app.qrme.studio.BeaconCard
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import kotlinx.coroutines.launch
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Point the phone at a beacon sticker and the profile appears **on the
 * sticker**, in the live camera feed. No tap, no page, no navigation.
 *
 * The counterpart of the iOS `BeaconScannerView`, and the same reasoning: a
 * stock camera app can only open a URL — that is the whole of the API surface
 * a QR code exposes to a third party. Drawing over a viewfinder means owning
 * the viewfinder, so this is the app that owns it. ML Kit reads the code,
 * `GET /b/{id}/card` answers, and the portrait is drawn on the bounding box
 * ML Kit reported, tracking the sticker as the phone moves.
 *
 * The AI mark is drawn from the same payload as the face, in the same
 * composable. An overlay that could show the portrait without the disclosure
 * would be the worst version of this feature: a synthetic person appearing in
 * the real world with nothing saying so.
 */
@Composable
fun BeaconScannerScreen(onOpen: (String) -> Unit, onClose: () -> Unit,
                        lang: String = "en") {
    val context = LocalContext.current
    var granted by remember {
        mutableStateOf(ContextCompat.checkSelfPermission(
            context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED)
    }
    val ask = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()) { granted = it }
    LaunchedEffect(Unit) { if (!granted) ask.launch(Manifest.permission.CAMERA) }

    if (!granted) {
        Box(Modifier.fillMaxSize().background(Qrme.Bg), Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(L10n.t("nbcn.camera", lang),
                    color = Qrme.Txt, fontSize = 15.sp)
                Text(L10n.t("nbcn.nothing", lang),
                    color = Qrme.T2, fontSize = 12.sp)
                ScanAction(L10n.t("nbcn.close", lang)) { onClose() }
            }
        }
        return
    }

    BeaconCameraSurface(onOpen = onOpen, onClose = onClose, lang = lang)
}

@SuppressLint("UnsafeOptInUsageError")
@Composable
private fun BeaconCameraSurface(onOpen: (String) -> Unit, onClose: () -> Unit,
                                lang: String) {
    val lifecycleOwner = LocalLifecycleOwner.current
    val density = LocalDensity.current
    val executor = remember { Executors.newSingleThreadExecutor() }
    val scanner = remember { BarcodeScanning.getClient() }
    val scope = rememberCoroutineScope()

    var card by remember { mutableStateOf<BeaconCard?>(null) }
    var box by remember { mutableStateOf<RectF?>(null) }
    // The camera delivers ~30 frames a second and every one of them sees the
    // same sticker. Without these two, the overlay would re-request
    // continuously and count a scan each time.
    val lastResolved = remember { arrayOfNulls<String>(1) }
    val inFlight = remember { AtomicBoolean(false) }

    DisposableEffect(Unit) {
        onDispose {
            executor.shutdown()
            scanner.close()
        }
    }

    Box(Modifier.fillMaxSize().background(Color.Black)) {
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { ctx ->
                val view = PreviewView(ctx).apply {
                    scaleType = PreviewView.ScaleType.FILL_CENTER
                }
                val providerFuture = ProcessCameraProvider.getInstance(ctx)
                providerFuture.addListener({
                    val provider = providerFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(view.surfaceProvider)
                    }
                    val analysis = ImageAnalysis.Builder()
                        .setBackpressureStrategy(
                            ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build()
                    analysis.setAnalyzer(executor) { proxy ->
                        analyse(proxy, scanner, view.width, view.height,
                            onBox = { r -> scope.launch { box = r } },
                            onPayload = { payload ->
                                val id = beaconId(payload)
                                if (id == null) {
                                    scope.launch { card = null; box = null }
                                    lastResolved[0] = null
                                } else if (id != lastResolved[0] &&
                                    inFlight.compareAndSet(false, true)) {
                                    lastResolved[0] = id
                                    scope.launch {
                                        card = runCatching {
                                            ApiClient.beaconCard(id)
                                        }.getOrNull()
                                        inFlight.set(false)
                                    }
                                }
                            },
                            onNothing = {
                                scope.launch { card = null; box = null }
                                lastResolved[0] = null
                            })
                    }
                    provider.unbindAll()
                    provider.bindToLifecycle(
                        lifecycleOwner, CameraSelector.DEFAULT_BACK_CAMERA,
                        preview, analysis)
                }, ContextCompat.getMainExecutor(ctx))
                view
            })

        val shown = card
        val where = box
        AnimatedVisibility(
            visible = shown != null && where != null,
            enter = fadeIn() + scaleIn(initialScale = 0.92f),
            exit = fadeOut()) {
            if (shown != null && where != null) {
                // Follow the sticker: ML Kit says where the code is, and the
                // portrait sits on it rather than in a fixed corner.
                val side = with(density) { where.width().toDp() }
                val x = with(density) { where.centerX().toDp() } - side / 2
                val y = with(density) { where.centerY().toDp() } - side * 1.25f
                Column(
                    Modifier.offset(x = x, y = y),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    if (shown.ageWall) {
                        // Nothing about the profile is in the payload to leak.
                        Box(
                            Modifier.size(side)
                                .clip(RoundedCornerShape(18.dp))
                                .background(Color.Black.copy(alpha = 0.72f)),
                            Alignment.Center) {
                            Text("18+", color = Color.White, fontSize = 34.sp,
                                fontWeight = FontWeight.Black)
                        }
                    } else {
                        Box(
                            Modifier.size(side)
                                .clip(RoundedCornerShape(18.dp))
                                .background(Qrme.Card),
                            Alignment.Center) {
                            Text(shown.initials, color = Qrme.BrandA,
                                fontSize = 34.sp, fontWeight = FontWeight.Bold)
                            Box(Modifier.align(Alignment.BottomStart)
                                .padding(6.dp)
                                .clip(CircleShape)
                                .background(Color.Black.copy(alpha = 0.75f))
                                .padding(horizontal = 8.dp, vertical = 4.dp)) {
                                Text(shown.watermark, color = Color.White,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold)
                            }
                        }
                        Text(shown.displayName, color = Color.White,
                            fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        if (shown.sharedRoom) {
                            Text(L10n.t("nbcn.shared", lang),
                                color = Color.White.copy(alpha = 0.8f),
                                fontSize = 11.sp)
                        }
                    }
                }
            }
        }

        Column(
            Modifier.align(Alignment.BottomCenter).fillMaxWidth()
                .padding(bottom = 34.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Box(Modifier.clip(CircleShape)
                .background(Color.Black.copy(alpha = 0.45f))
                .padding(horizontal = 14.dp, vertical = 8.dp)) {
                Text(L10n.t(if (shown == null) "nbcn.point" else "nbcn.tap", lang),
                    color = Color.White.copy(alpha = 0.85f), fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold)
            }
            ScanAction(L10n.t(if (shown?.openUrl != null) "corner.open" else "nbcn.close", lang)) {
                val url = shown?.openUrl
                if (url != null) onOpen(url) else onClose()
            }
        }
    }
}

@ExperimentalGetImage
@SuppressLint("UnsafeOptInUsageError")
private fun analyse(
    proxy: ImageProxy,
    scanner: com.google.mlkit.vision.barcode.BarcodeScanner,
    viewWidth: Int,
    viewHeight: Int,
    onBox: (RectF) -> Unit,
    onPayload: (String) -> Unit,
    onNothing: () -> Unit,
) {
    val media = proxy.image
    if (media == null) {
        proxy.close()
        return
    }
    val image = InputImage.fromMediaImage(
        media, proxy.imageInfo.rotationDegrees)
    scanner.process(image)
        .addOnSuccessListener { codes ->
            val qr = codes.firstOrNull {
                it.format == Barcode.FORMAT_QR_CODE && it.rawValue != null
            }
            if (qr == null) {
                onNothing()
            } else {
                qr.boundingBox?.let { rect ->
                    // ML Kit reports in the analysis image's coordinate space,
                    // which is rotated relative to the view and usually a
                    // different resolution. Map it before drawing, or the
                    // portrait lands somewhere the sticker is not.
                    val rotated = proxy.imageInfo.rotationDegrees % 180 != 0
                    val srcW = if (rotated) proxy.height else proxy.width
                    val srcH = if (rotated) proxy.width else proxy.height
                    if (srcW > 0 && srcH > 0 && viewWidth > 0 && viewHeight > 0) {
                        // FILL_CENTER crops the longer axis, so both axes take
                        // the same scale and the excess is split evenly.
                        val scale = maxOf(viewWidth.toFloat() / srcW,
                            viewHeight.toFloat() / srcH)
                        val dx = (viewWidth - srcW * scale) / 2f
                        val dy = (viewHeight - srcH * scale) / 2f
                        onBox(RectF(
                            rect.left * scale + dx, rect.top * scale + dy,
                            rect.right * scale + dx, rect.bottom * scale + dy))
                    }
                }
                onPayload(qr.rawValue!!)
            }
        }
        .addOnCompleteListener { proxy.close() }
}

/**
 * A beacon's printed QR encodes `<base>/b/<id>`. Anything else is somebody's
 * Wi-Fi password and is left alone.
 */
internal fun beaconId(payload: String): String? {
    val parts = payload.substringBefore('?').trimEnd('/').split('/')
        .filter { it.isNotEmpty() }
    if (parts.size < 2) return null
    if (parts[parts.size - 2] != "b") return null
    val id = parts.last()
    return if (id.startsWith("bcn_")) id else null
}

/**
 * The scanner's own button. `SmallAction` in Screens.kt is file-private, and
 * widening it just to reach it from here would be the wrong trade.
 */
@Composable
private fun ScanAction(text: String, onClick: () -> Unit) {
    Box(
        Modifier.clip(CircleShape).background(Qrme.BrandA)
            .clickable { onClick() }
            .padding(horizontal = 16.dp, vertical = 10.dp),
    ) {
        Text(text, color = Color.White, fontSize = 13.sp,
            fontWeight = FontWeight.Bold)
    }
}

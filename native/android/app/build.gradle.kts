plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "app.qrme.studio"
    compileSdk = 34

    defaultConfig {
        applicationId = "app.qrme.studio"
        minSdk = 26
        targetSdk = 34
        versionCode = 90000
        versionName = "0.90.0"

        // Where content-free problem reports go, and the token to post them
        // with. The console's equivalent is the `define` block in
        // app/vite.config.ts. Empty is the default and the stronger one: an
        // install with no address has nowhere to send, and there is no flag
        // for a later mistake to switch on.
        //
        //   ./gradlew assembleRelease -PproblemCollector=https://gw.example.com \
        //                             -PproblemToken=...
        buildConfigField("String", "PROBLEM_COLLECTOR",
            "\"${project.findProperty("problemCollector") ?: ""}\"")
        buildConfigField("String", "PROBLEM_TOKEN",
            "\"${project.findProperty("problemToken") ?: ""}\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true; buildConfig = true }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.09.02")
    implementation(composeBom)
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-compose:1.9.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.5")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    // The in-camera beacon overlay: CameraX owns the viewfinder, ML Kit reads
    // the code. The barcode model is bundled rather than downloaded on demand,
    // so a first scan works without Play Services fetching anything.
    implementation("androidx.camera:camera-camera2:1.3.4")
    implementation("androidx.camera:camera-lifecycle:1.3.4")
    implementation("androidx.camera:camera-view:1.3.4")
    implementation("com.google.mlkit:barcode-scanning:17.3.0")
    // Passkey signing (docs/signatures.md). Credential Manager is the only
    // supported path to a platform authenticator on modern Android; the
    // play-services-auth artifact is what backfills it below API 34.
    implementation("androidx.credentials:credentials:1.3.0")
    implementation("androidx.credentials:credentials-play-services-auth:1.3.0")
    // The live desk view. Compose has no async image loader of its own.
    implementation("io.coil-kt:coil-compose:2.7.0")
    debugImplementation("androidx.compose.ui:ui-tooling")
}

package app.qrme.studio

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Face
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.viewmodel.compose.viewModel
import app.qrme.studio.ui.Qrme
import app.qrme.studio.ui.QrmeTheme
import app.qrme.studio.ui.ChatScreen
import app.qrme.studio.ui.ComposeScreen
import app.qrme.studio.ui.OverviewScreen
import app.qrme.studio.ui.PostsScreen
import app.qrme.studio.ui.RobotsScreen
import app.qrme.studio.ui.SettingsScreen
import app.qrme.studio.ui.WelcomeScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            QrmeTheme {
                val vm: StudioViewModel = viewModel()
                if (!vm.isSignedIn) {
                    WelcomeScreen(vm)
                } else {
                    HomeShell(vm)
                }
            }
        }
    }
}

@androidx.compose.runtime.Composable
private fun HomeShell(vm: StudioViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf(
        Triple("Overview", Icons.Filled.GridView, 0),
        Triple("Chat", Icons.Filled.Chat, 1),
        Triple("Compose", Icons.Filled.Edit, 2),
        Triple("Posts", Icons.Filled.List, 3),
        Triple("Robots", Icons.Filled.Face, 4),
        Triple("Settings", Icons.Filled.Settings, 5),
    )
    Scaffold(
        containerColor = Qrme.ScrBot,
        bottomBar = {
            NavigationBar(containerColor = Color(0xFF0B1220)) {
                tabs.forEach { (label, icon, index) ->
                    NavigationBarItem(
                        selected = tab == index,
                        onClick = { tab = index },
                        icon = { Icon(icon, contentDescription = label) },
                        label = { Text(label) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Qrme.BrandA,
                            selectedTextColor = Qrme.BrandA,
                            unselectedIconColor = Qrme.T2,
                            unselectedTextColor = Qrme.T2,
                            indicatorColor = Color(0x337C5CFF),
                        ),
                    )
                }
            }
        },
    ) { pad ->
        Box(Modifier.fillMaxSize().background(Qrme.Bg).padding(pad)) {
            when (tab) {
                0 -> OverviewScreen(vm)
                1 -> ChatScreen(vm)
                2 -> ComposeScreen(vm)
                3 -> PostsScreen(vm)
                4 -> RobotsScreen(vm)
                else -> SettingsScreen(vm)
            }
        }
    }
}

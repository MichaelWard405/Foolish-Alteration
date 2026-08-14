import app from "ags/gtk4/app"
import style from "./style.scss"
import { TopBar, BottomBar } from "./widget/Desktop_Bars"
import { AppLauncher } from "./widget/AppLauncher" // <-- Import the new launcher!

app.start({
  css: style,
  main() {
    // Top and Bottom bars (Drawn on every monitor)
    app.get_monitors().map((monitor) => {
      TopBar(monitor)
      BottomBar(monitor)
    })

    // App Launcher (Only ONE global instance drawn centrally!)
    AppLauncher()
  },
})

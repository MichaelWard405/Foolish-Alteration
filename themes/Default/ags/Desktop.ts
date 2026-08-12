import app from "ags/gtk4/app"
import style from "./style.scss"
import { TopBar, BottomBar } from "./widget/Desktop_Bars"

app.start({
  css: style,
  main() {
    app.get_monitors().map((monitor) => {
      TopBar(monitor)
      BottomBar(monitor)
    })
  },
})

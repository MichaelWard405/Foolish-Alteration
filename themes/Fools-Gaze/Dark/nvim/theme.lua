return {
  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    opts = {
      color_overrides = {
        all = {
          base = "#141111",
          mantle = "#100d0d",
          crust = "#0c0a0a",
          red = "#ff6b6b",
          peach = "#ff6b6b",
        },
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "catppuccin",
    },
  },
}

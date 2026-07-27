-- Clear any existing highlights
vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") then
    vim.cmd("syntax reset")
end

-- Name your custom theme
vim.g.colors_name = "fools_gaze"

-- Define your signature palette
local palette = {
    bg = "#000000",       -- Deep Black background
    fg = "#e0e0e0",       -- Crisp white/grey text
    accent = "#ff6b6b",   -- Cyber Red
    comment = "#444444",  -- Stealthy grey
    mantle = "#0a0a0a",   -- Slightly lighter black for floating windows
    crust = "#111111",    -- Borders and statuslines
    selection = "#2a1111", -- Faint red tint for highlighted text
}

-- Map the colors to Neovim and LazyVim UI elements
local highlights = {
    -- Base UI
    Normal = { bg = palette.bg, fg = palette.fg },
    NormalFloat = { bg = palette.mantle, fg = palette.fg },
    LineNr = { fg = palette.comment, bg = palette.bg },
    CursorLine = { bg = palette.mantle },
    CursorLineNr = { fg = palette.accent, bold = true },
    Visual = { bg = palette.selection },
    
    -- Syntax
    Comment = { fg = palette.comment, italic = true },
    String = { fg = "#aaaaaa" },
    Number = { fg = palette.accent },
    Boolean = { fg = palette.accent, bold = true },
    Keyword = { fg = palette.accent, bold = true, italic = true },
    Function = { fg = palette.fg, bold = true },
    Identifier = { fg = palette.fg },
    Statement = { fg = palette.accent },
    Type = { fg = palette.accent },
    
    -- UI Accents & Errors
    ErrorMsg = { fg = palette.accent, bg = palette.crust },
    WarningMsg = { fg = palette.accent },
    TelescopeBorder = { fg = palette.accent, bg = palette.bg },
    TelescopeNormal = { bg = palette.bg },
    StatusLine = { bg = palette.crust, fg = palette.fg },
    
    -- TreeSitter (Modern Syntax Highlighting)
    ["@variable"] = { fg = palette.fg },
    ["@keyword"] = { fg = palette.accent, italic = true },
    ["@function"] = { fg = palette.fg, bold = true },
    ["@string"] = { fg = "#aaaaaa" },
    ["@comment"] = { fg = palette.comment, italic = true },
    
    -- LazyVim Specific overrides
    LazyNormal = { bg = palette.bg },
    MasonNormal = { bg = palette.bg },
}

-- Apply the highlights
for group, opts in pairs(highlights) do
    vim.api.nvim_set_hl(0, group, opts)
end

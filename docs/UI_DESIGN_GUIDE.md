# UI Design Guide for Claude Code

> How to get professional-quality UI designs instead of generic AI aesthetics.

## The Problem with Default AI Design

AI coding tools tend to produce:
- Purple/blue gradients everywhere
- Generic, "AI-looking" interfaces
- Inconsistent styling
- Poor typography choices
- Missing animations and polish

## Solution: Front-End Design Skill

The **Front-End Design Skill** dramatically improves UI quality by teaching Claude to create distinctive, production-grade interfaces.

### Installation

```bash
# In Claude Code, run these commands:

# 1. Add the skills marketplace
/add-skill-marketplace https://skills.anthropic.com

# 2. Install the front-end design skill
/install-skill front-end-design
```

### Usage

Simply invoke the skill when working on UI:

```
Use the front-end design skill to improve the design of this landing page.
```

Or with a reference image:

```
Use the front-end design skill to improve the design of this page
following the attached screenshot.
[paste screenshot]
```

---

## Design Principles

### The "Black, White, and One Color" Rule

Start every design with:
- **Black** - Text, dark backgrounds
- **White** - Light backgrounds, contrast
- **One accent color** - CTAs, highlights, branding

Add more colors only after establishing this foundation.

### What Good AI-Generated UI Includes

When the skill works well, you'll see:
- ✅ Thoughtful typography choices
- ✅ Subtle animations and hover effects
- ✅ Consistent spacing and padding
- ✅ Soft shadows with blur
- ✅ Subtle background patterns (grids, gradients)
- ✅ Glow effects on interactive elements
- ✅ Smooth scroll behavior
- ✅ Coherent color palette

### What to Watch For

Common issues to fix manually:
- ❌ Buttons that don't stand out on backgrounds
- ❌ Missing call-to-action prominence
- ❌ Emoji icons instead of proper icon library
- ❌ Text alignment issues
- ❌ Inconsistent section styling

---

## Design Reference Sources

### For Inspiration

| Source | Best For | URL |
|--------|----------|-----|
| **Dribbble** | UI design patterns, landing pages | [dribbble.com](https://dribbble.com) |
| **V0.dev** | Component design systems | [v0.dev](https://v0.dev) |
| **Pinterest** | App design inspiration | [pinterest.com](https://pinterest.com) |
| **Mobbin** | Mobile app patterns | [mobbin.com](https://mobbin.com) |
| **Awwwards** | Award-winning web design | [awwwards.com](https://awwwards.com) |

### How to Use References

1. Find a design you like on Dribbble/Pinterest
2. Take a screenshot (Cmd+Ctrl+Shift+4 on Mac copies to clipboard)
3. Paste into Claude Code with your prompt
4. Ask Claude to follow the reference's style

**Example prompt:**
```
Use the front-end design skill to redesign this dashboard
following the attached screenshot. Match the typography,
spacing, and color palette.
[paste screenshot]
```

---

## Creating a Design System

For even better results, create a design system in your codebase:

### 1. Design Tokens File

Create `src/styles/tokens.css` or similar:

```css
:root {
  /* Colors */
  --color-primary: #0066ff;
  --color-secondary: #6b7280;
  --color-background: #ffffff;
  --color-surface: #f9fafb;
  --color-text: #111827;
  --color-text-muted: #6b7280;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;

  /* Radii */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

### 2. Document in CLAUDE.md

Add to your CLAUDE.md:

```markdown
## Design System

Use design tokens from `src/styles/tokens.css` for all styling.
- Always use CSS variables for colors, spacing, shadows
- Follow the established typography scale
- Maintain consistent border radii
- Use the shadow scale for elevation
```

### 3. Reference When Building UI

```
Build a user profile card component following our design system
in src/styles/tokens.css. Use the front-end design skill for
the implementation.
```

---

## Workflow Summary

### For New Projects

1. Build functionality first (don't worry about design)
2. Install front-end design skill
3. Find 2-3 reference designs you like
4. Apply skill with references to improve UI
5. Iterate on specific sections

### For Existing Projects

1. Install front-end design skill
2. Identify pages/components needing improvement
3. Gather reference screenshots
4. Apply skill section by section
5. Fix any inconsistencies manually

### Pro Tips

- **One section at a time**: Better results than redesigning everything at once
- **Be specific**: "Improve the hero section" > "Improve the design"
- **Provide context**: "This is a B2B SaaS for developers" helps set the tone
- **Iterate**: First pass rarely perfect, refine specific elements
- **Save good outputs**: Screenshot successful designs for future reference

---

## Common Style Transformations

The skill can transform between styles:

| From | To | Prompt Hint |
|------|-----|-------------|
| Generic AI | Professional | "Create a clean, professional design" |
| Brutalist | Soft Modern | "Use soft shadows, rounded corners, gradients" |
| Cluttered | Minimal | "Simplify with more whitespace" |
| Flat | Dimensional | "Add depth with shadows and layers" |
| Corporate | Playful | "Make it more friendly and approachable" |

---

## Troubleshooting

### Still Getting Purple Gradients?

- Explicitly say "avoid purple gradients and generic AI aesthetics"
- Provide a reference screenshot with your preferred style
- Specify your color palette in the prompt

### Inconsistent Sections?

- Redesign one section at a time
- Reference earlier successful sections: "Match the style of the hero section"
- Create and reference a design system

### Icons Look Wrong?

- Specify icon library: "Use Lucide icons" or "Use Heroicons"
- Avoid emoji icons: "Use proper SVG icons, not emojis"

---

*This guide synthesizes best practices from the Claude Code community and professional designers using AI tools.*

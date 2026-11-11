---
name: Pro-Ter-Pa
description: A photographic monograph for a local landscape maker, grounded in real work and direct contact.
colors:
  forest: "#254c35"
  lime: "#d8e66b"
  ink: "#24392d"
  paper: "#f8f9f4"
  muted: "#586557"
  line: "#cbd2c7"
  white: "#fff"
  soft-sage: "#e8eddf"
typography:
  display:
    fontFamily: '"Arial Narrow", "Trebuchet MS", Arial, sans-serif'
    fontSize: "clamp(48px, 6.6vw, 96px)"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "-.045em"
  headline:
    fontFamily: '"Arial Narrow", "Trebuchet MS", Arial, sans-serif'
    fontSize: "clamp(34px, 4.2vw, 62px)"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "-.045em"
  title:
    fontFamily: '"Arial Narrow", "Trebuchet MS", Arial, sans-serif'
    fontSize: "clamp(27px, 2.7vw, 39px)"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "-.045em"
  body:
    fontFamily: '"Trebuchet MS", Arial, sans-serif'
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: '"Trebuchet MS", Arial, sans-serif'
    fontSize: "14px"
    fontWeight: 700
spacing:
  gutter: "clamp(22px, 5vw, 88px)"
components:
  button-primary:
    backgroundColor: "{colors.forest}"
    textColor: "{colors.white}"
    padding: "13px 22px"
  button-primary-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    padding: "13px 22px"
  nav-contact:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
    padding: "12px 20px"
  service-row:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    padding: "34px 0"
  hero-photo-caption:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.ink}"
    padding: "18px 26px"
---

# Design System: Pro-Ter-Pa

## Overview

**Creative North Star: "The Landscape-Maker's Photographic Monograph"**

Pro-Ter-Pa presents outdoor work with the confidence of a working landscape journal: real project photography leads, practical words explain the craft, and the interface stays open enough for the work to breathe. The visual direction is grounded in the shipped candidate 3, seed `3cd0af47`: a photographic, facing-page composition rather than a generic contractor template.

Woodland green, chalky paper and fresh chartreuse carry the identity. Bold, locally available sans-serif typography and unboxed rows make the site direct and useful; actual project photographs provide evidence rather than decoration. The home-page opening pairs its promise on the left with a real chantier photograph on the right, with a lime caption; service paths and direct contact follow. Preserve the existing photo archive, footer, and distinct contact and legal contexts.

**Key Characteristics:**
- Practical, bold local sans-serif typography.
- Real landscape and chantier photography as the primary visual proof.
- Open rows, calm paper surfaces, and restrained green/chartreuse accents.
- Clear service routes and direct telephone and email contact.

## Colors

Chalk paper and soft sage make room for woodland green; chartreuse is reserved for crisp emphasis and image captions.

### Primary
- **Woodland Green** (`{colors.forest}`): Main action color and deep section field, including service actions and the strengths section.

### Secondary
- **Fresh Chartreuse** (`{colors.lime}`): High-visibility accent for the photo caption and contact band.

### Neutral
- **Deep Green Ink** (`{colors.ink}`): Default text and the dark footer; also supports the contact navigation action.
- **Chalk Paper** (`{colors.paper}`): Site canvas and header background.
- **Soft Sage** (`{colors.soft-sage}`): Quiet alternate section and note surface, including photo, page-title, and contact-note areas.
- **Muted Leaf** (`{colors.muted}`): Supporting copy, captions, and secondary explanatory text.
- **Pale Divider** (`{colors.line}`): Fine separators between open service rows and navigation/footer structure.
- **White** (`{colors.white}`): Reverse type on deep green surfaces.

**The Real-Work Rule.** Let the photographs carry the variety of the landscape; keep the interface palette to the established greens, chalk, sage, and chartreuse.

## Typography

**Display Font:** Arial Narrow (with Trebuchet MS, Arial, sans-serif fallbacks)  
**Body Font:** Trebuchet MS (with Arial, sans-serif fallbacks)  
**Label/Mono Font:** No distinct mono face; labels use the body sans.

**Character:** Condensed, heavy headings give the practical voice a clear silhouette. Trebuchet MS keeps paragraphs and navigation familiar and legible.

### Hierarchy
- **Display** (700, `clamp(48px, 6.6vw, 96px)`, 1.04 line height): Oversized home-page promise.
- **Headline** (700, `clamp(34px, 4.2vw, 62px)`, 1.04 line height): Section headings.
- **Title** (700, `clamp(27px, 2.7vw, 39px)`, 1.04 line height): Service and supporting headings.
- **Body** (400, 17px, 1.65 line height): Main explanatory copy; the base size becomes 16px on narrow screens. Paragraphs are kept to a readable measure, generally no wider than 72ch.
- **Label** (700, 14px): Navigation and compact metadata; photo captions use a smaller 13px size.

**The Practical Contrast Rule.** Keep display hierarchy bold and compact; supporting prose remains relaxed and readable rather than adopting the heading face.

## Layout

The content uses a fluid page gutter (`clamp(22px, 5vw, 88px)`) and generous section spacing. At wide widths the home hero is a two-column, facing-page composition (copy and actions beside a slightly wider photograph); at 850px and below it becomes a stacked story. Service descriptions sit in open, horizontally ruled rows, while the photo gallery uses three columns on wide screens and reduces to two on tablet and one where needed. The header navigation becomes a toggled vertical menu at 850px and below. Contact and service-detail layouts also collapse to single columns on smaller screens. At 520px the body size, button padding, row layout, gallery gaps, and footer layout tighten for phone use.

## Elevation & Depth

The interface is flat by default: it uses no drop-shadow vocabulary. Separation comes from paper and sage section fields, fine borders, reversed green surfaces, and the depth and cropping of real photographs. The image viewer uses a dark modal backdrop as a functional focus state. A thin green underline marks navigation hover and current-page state.

**The Flat-By-Default Rule.** Use tonal fields, borders, and photography—not decorative card shadows—to distinguish content.

## Shapes

The form language is square-edged and workmanlike: controls, image frames, notes, and sections use no rounded-corner scale. Fine rules define rows and boundaries. Photographs stay rectangular and are cropped to suit their role; the gallery is mostly 4:3, with selected wide images allowed to span columns.

## Components

### Buttons
- **Character:** Confident rectangular actions with a directional arrow.
- **Shape:** Square corners; no radius.
- **Primary:** Woodland green with white text, a thin matching border, and `13px 22px` padding; minimum height 50px.
- **Hover / Focus:** Hover shifts the fill and border to deep green ink. Keyboard focus uses the site-wide visible outline.
- **Secondary:** Transparent with ink text and pale divider border; hover changes to chartreuse.

### Navigation
- **Style:** Bold, compact sans-serif links on the chalk-paper header, with generous vertical click padding.
- **State:** Hover and current page use a thin woodland underline. The project-contact link is a filled ink action.
- **Mobile:** At 850px and below, a menu button opens the paper-colored vertical navigation; Escape, link selection, and focus leaving the menu close it.

### Service Rows
- **Character:** Open, ruled paths into the three actual service pages.
- **Shape:** No enclosing card or radius; fine divider rules and generous vertical padding.
- **Behavior:** Title, supporting description, and arrow lead to the corresponding service route. Hover underlines the title and moves the arrow slightly.
- **Responsive:** On narrow screens the description sits below the title and arrow.

### Hero Photograph and Caption
- **Character:** A real chantier photograph acts as the facing page to the opening promise.
- **Treatment:** Edge-to-edge image crop with a chartreuse caption bar at the bottom, carrying project and location context.
- **Responsive:** The composition stacks on narrow screens while retaining the image and caption.

### Photo Gallery
- **Character:** Real project imagery with short descriptive captions; imagery remains the proof, not a decorative background.
- **Treatment:** Rectangular cropped thumbnails with open captions below. Selected images receive a wider span on larger screens.
- **Behavior:** Activating a photo opens the keyboard-operable lightbox with caption, counter, previous/next controls, and return focus to the opener.

### Contact Paths
- **Character:** A chartreuse contact band makes the practical next step immediate.
- **Actions:** Keep the service/contact route, telephone link, and email link connected to their real destinations. Do not substitute a decorative or nonfunctional form.

### Footer and Preserved Context
- Keep the existing footer's business identity, service and gallery links, phone, email, address, hours, and legal/privacy link.
- Preserve the photo archive in its existing gallery context and retain the separate contact and legal explanations for the V2 and original site.

## Do's and Don'ts

### Do:
- **Do** use real Pro-Ter-Pa photographs as the leading visual evidence.
- **Do** maintain the chalk-paper, woodland-green, soft-sage, and chartreuse palette.
- **Do** leave service paths open and scannable, with thin rules rather than cards.
- **Do** keep telephone and email links pointed to the shipped direct-contact destinations.
- **Do** preserve the existing footer, photo archive, and contact/legal distinctions.

### Don't:
- **Don't** replace the monograph direction with a generic contractor template or decorative stock imagery.
- **Don't** invent pricing, testimonials, services, or claims.
- **Don't** add rounded cards, decorative shadows, or a fake contact form.
- **Don't** remove the original photo archive or collapse the distinct contact and legal contexts.

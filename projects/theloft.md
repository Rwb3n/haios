# The Loft – Landing Page Specification

> **Document Version**: 0.1-draft  
> **Author**: Planner (AI)  
> **Last Updated**: 2025-07-21  
> **Trace-ID**: THELOFT-LP-20250721  
> **Context Source**: Screenshot provided by user (home-improvement landing page)  

---

## 1. Purpose
A complete, implementation-ready specification for “The Loft” marketing landing page, decomposed from the supplied screenshot. This document eliminates ambiguity so that implementation agents can deterministically translate it into code and design assets.

---

## 2. Assumptions & Constraints
| Item | Description | Confidence | Self-Critique |
|------|-------------|------------|---------------|
| A-1  | Target audience is UK homeowners seeking quality home improvements. | 0.7 | May vary by region – validate copy localization needs. |
| A-2  | CMS is **not** required; content can be hard-coded for MVP. | 0.6 | Future marketing iteration may need CMS integration. |
| A-3  | Design should be responsive for desktop, tablet, and mobile breakpoints. | 0.9 | Mobile layout inferred; ensure separate QA. |
| C-1  | Color palette and typography are derived directly from screenshot; hex values to be sampled and confirmed in design system. | 0.8 | Precise values need designer confirmation. |

---

## 3. Dependencies & Risks
| ID | Dependency / Risk | Likelihood | Impact | Mitigation | Confidence |
|----|-------------------|------------|--------|------------|------------|
| D-1 | Access to high-resolution imagery for hero and gallery. | Medium | High | Engage photographer / stock sourcing early. | 0.7 |
| R-1 | Contact form backend endpoint availability. | Low | High | Stub API in Foundation Layer; switch to prod later. | 0.8 |
| R-2 | Accessibility (WCAG 2.2) compliance gaps due to visual-only cues. | Medium | Medium | Include alt text & high-contrast mode in UI spec. | 0.6 |

---

## 4. Distributed Systems Protocol Compliance (DSPC)
This static landing page consumes minimal backend services (contact form submission). It must:
1. Use HTTPS for all requests.
2. Emit a standard JSON payload `{name, email, phone, message}` to `/api/contact`.
3. Expect `202 Accepted` with `{submissionId}` response for async processing.
4. Include `X-Trace-ID` header propagating the above Trace-ID for observability.

---

## 5. Information Architecture
1. **Hero** – Branding, headline, sub-headline, CTA button.
2. **About / Specialists** – Intro paragraph + 4-image gallery (services showcase).
3. **Key Metrics** – 4 numeric highlights (years, projects, trades, satisfaction).
4. **What We Do** – Service description & bullet list.
5. **Portfolio / Case Studies** – 3 feature cards with image, title, copy, author avatar.
6. **Testimonials** – 6 client review cards.
7. **FAQ** – Accordion with 7 common questions.
8. **Contact / Get in Touch** – Address, phone, email + form.
9. **Footer** – Logo, quick links, social thumbnails, copyright.

---

## 6. Component Specifications

### 6.1 Hero Section
| Property | Value |
|----------|-------|
| Component-ID | `hero-primary` |
| Layout | Two-column (text left, feature image right) on desktop; stacked on mobile. |
| Headline | “Your trusted partner for quality home improvement” |
| Sub-copy | “Helping you create a better living experience through exceptional craftsmanship and personalised service.” |
| CTA | Primary button labelled **“Get in touch”** – scrolls to Contact section. |
| Media | Lifestyle kitchen interior photo, 16:9 aspect. |
| Animation | Fade-in on scroll (duration 0.6 s, ease-out). |
| Acceptance Criteria | Text matches exactly; CTA functional; image loads <200 ms (LCP). |

### 6.2 Specialist Intro & Gallery
| Property | Value |
| Component-ID | `about-specialists` |
| Copy | “Western Sydney’s most trusted home improvement partner, dedicated to...” (full paragraph from screenshot). |
| Gallery | 4 equally sized cards (Kitchen, Hallway, Exterior, Modern facade). |
| Interaction | Hover zoom 1.05 scale; tap opens lightbox (mobile optional). |

### 6.3 Key Metrics
| Stat | Label | Value |
|------|-------|-------|
| `stat-years` | Years experience | 8 |
| `stat-projects` | Projects completed per year | 26 |
| `stat-trades` | In-house tradespeople | 30 |
| `stat-satisfaction` | Client satisfaction | 100 % |
Formatting: Large numeric (4 rem), caption (0.875 rem), flex grid 4 columns, wraps to 2-2 on tablet.

### 6.4 “What We Do” Services
Bullet list icons:
- Loft Conversions
- Extensions
- Refits
- Renovations
- Rental Works

Include supporting paragraph (as screenshot) and full-width supporting image left, text right (switch order on alternate rows for mobile).

### 6.5 Portfolio / Case Studies
Three cards within horizontal scroll container (snap-x on mobile):
1. **Modern kitchen refit** – Feature image, 120-word description, tags `kitchen`, `refit`, author avatar & name *Mark Taylor*.
2. **External garden path build** – Same structure, author *Rachel Wong*.
3. **Bathroom renovation** – Same structure, author *Liam Smith*.

### 6.6 Testimonials
Grid of 6 cards (2 rows × 3). Each card includes 5-star rating icons, 40-word quote, client name & avatar.

### 6.7 FAQ Accordion
Accordion component `faq-accordion` with the following Q&A (truncate answers to ~30 words for spec):
1. **“What areas do you service?”** – We operate across London & suburbs...
2. **“How long does a typical project take?”** – Timelines vary; average 6-12 weeks...
3. **“Do you offer free quotes?”** – Yes, complimentary site visit...
4. **“Do I need planning permission?”** – Our team handles planning...
5. **“Do you provide guarantees?”** – All work covered by 10-year guarantee...
6. **“Can I stay in my home while work is done?”** – Often yes, depends on scope...
7. **“How can I get started?”** – Contact us via form or phone...

### 6.8 Contact / Get in Touch
Form fields: `Name*` (input text), `Email*` (email), `Phone` (tel), `Message*` (textarea 5 rows), Submit button (loading state). Validation: required `*`, email regex. Success: Redirect to `/thank-you` with query `id=submissionId`.

Static info block (left column):
- Address: 13 High Street, London W1F 9LN
- Email: hello@theloft.co.uk
- Telephone: 01745 889 123

### 6.9 Footer
Sections: Logo, Quick links (About, Services, Portfolio, FAQ, Contact), miniature Instagram thumbnails (4 images), copyright `© 2025 The Loft`. Background: #0E0E0E, text muted #8A8A8A.

---

## 7. Design Token Dictionary

> **Note**: All token names follow the `kebab-case` CSS custom property convention and are intended for use with a style-dictionary or design-system pipeline.

### 7.1 Colour Palette
| Token | Role | Sample |
|-------|------|--------|
| `--color-primary` | Brand accent / CTA | `#E27444` |
| `--color-primary-hover` | Hover state for primary elements | `#D5683E` |
| `--color-primary-active` | Active/pressed primary | `#C75A34` |
| `--color-secondary` | Dark surfaces (footer, nav) | `#141414` |
| `--color-background` | Page background | `#FFFFFF` |
| `--color-surface` | Card & section surfaces | `#F6F6F6` |
| `--color-text-primary` | Main body copy | `#222222` |
| `--color-text-secondary` | Muted captions, metadata | `#666666` |
| `--color-text-inverse` | Text on dark surfaces | `#FFFFFF` |
| `--color-neutral-100` | `#FFFFFF` |
| `--color-neutral-200` | `#F9F9F9` |
| `--color-neutral-300` | `#E6E6E6` |
| `--color-neutral-400` | `#CCCCCC` |
| `--color-neutral-500` | `#999999` |
| `--color-neutral-600` | `#666666` |
| `--color-neutral-700` | `#444444` |
| `--color-neutral-800` | `#2B2B2B` |
| `--color-neutral-900` | `#0E0E0E` |
| `--color-success` | Semantic ‑ success | `#2E7D32` |
| `--color-warning` | Semantic ‑ warning | `#ED6C02` |
| `--color-error` | Semantic ‑ error | `#D32F2F` |
| `--color-info` | Semantic ‑ info | `#0288D1` |

### 7.2 Typography Scale
| Token | Usage | Value |
|-------|-------|-------|
| `--font-family-heading` | H1–H6 | "Playfair Display", serif |
| `--font-family-body` | Paragraphs | "Inter", sans-serif |
| `--font-weight-regular` | Base weight | 400 |
| `--font-weight-medium` | Emphasis | 500 |
| `--font-weight-bold` | Headings / strong | 700 |
| `--font-size-xxl` | Hero headings | 4.5rem |
| `--font-size-xl` | H1 | 3.5rem |
| `--font-size-lg` | H2 | 2.5rem |
| `--font-size-md` | H3 | 1.75rem |
| `--font-size-base` | Body (p) | 1rem |
| `--font-size-sm` | Small text | 0.875rem |
| `--font-size-xs` | Micro text | 0.75rem |
| `--line-height-tight` | Display headings | 1.1 |
| `--line-height-regular` | Body copy | 1.45 |
| `--line-height-loose` | Long-form | 1.6 |
| `--letter-spacing-wide` | Uppercase buttons | 0.05em |

Mapping example: `h1 {font: var(--font-weight-bold) var(--font-size-xl)/var(--line-height-tight) var(--font-family-heading);}`

### 7.3 Spacing & Sizing
| Token | Rem | Px equivalent |
|-------|-----|---------------|
| `--space-0` | 0 | 0 |
| `--space-1` | 0.25rem | 4px |
| `--space-2` | 0.5rem | 8px |
| `--space-3` | 1rem | 16px |
| `--space-4` | 1.5rem | 24px |
| `--space-5` | 2rem | 32px |
| `--space-6` | 3rem | 48px |

Additional sizing tokens:
* `--radius-sm`: 4px  
* `--radius-md`: 8px  
* `--radius-lg`: 12px  
* `--border-width`: 1px solid var(--color-neutral-300)
* `--shadow-sm`: 0 1px 2px rgba(0,0,0,.05)  
* `--shadow-md`: 0 4px 6px rgba(0,0,0,.1)  
* `--shadow-lg`: 0 10px 15px rgba(0,0,0,.15)

### 7.4 Animation & Motion
| Token | Purpose | Value |
|-------|---------|-------|
| `--anim-duration-fast` | Hover, micro-interactions | 0.2s |
| `--anim-duration-medium` | Standard transitions | 0.4s |
| `--anim-duration-slow` | Hero reveals | 0.6s |
| `--anim-ease-standard` | Default easing | cubic-bezier(0.4,0,0.2,1) |
| `--anim-ease-in` | Speed-in | cubic-bezier(0.4,0,1,1) |
| `--anim-ease-out` | Speed-out | cubic-bezier(0,0,0.2,1) |
| `--anim-key-fade-in` | Keyframes ref | `@keyframes fade-in {from{opacity:0} to{opacity:1}}` |

### 7.5 Component Tokens
| Component | Token | Value |
|-----------|-------|-------|
| **Button** | `--button-height` | 48px |
|           | `--button-padding-x` | 1.5rem |
|           | `--button-radius` | var(--radius-md) |
|           | `--button-shadow` | var(--shadow-sm) |
| **Card** | `--card-padding` | var(--space-4) |
|          | `--card-radius` | var(--radius-lg) |
|          | `--card-shadow` | var(--shadow-lg) |
|          | `--card-background` | var(--color-surface) |
| **Accordion** | `--accordion-icon-size` | 1.25rem |
|              | `--accordion-content-padding` | var(--space-3) |

### 7.6 Layout & Breakpoints
| Token | Min-Width |
|-------|-----------|
| `--breakpoint-xs` | 480px |
| `--breakpoint-sm` | 640px |
| `--breakpoint-md` | 768px |
| `--breakpoint-lg` | 1024px |
| `--breakpoint-xl` | 1280px |

Grid container:
* `--container-max-width`: 1140px  
* `--container-padding-x`: var(--space-4)

### 7.7 Page Templates
| Template | Purpose | Key Regions & Components |
|----------|---------|--------------------------|
| `template-landing` | Marketing landing (this spec) | hero → about → stats → services → portfolio → testimonials → FAQ → contact → footer |
| `template-case-study` | Detailed project showcase | hero (project image + intro) → gallery (carousel) → project details (grid) → testimonial → CTA |
| `template-thank-you` | Post-form confirmation | confirmation message → secondary CTA → social links |

Each template extends foundational tokens; only overrides (e.g., background-color) are specified at the page level.

---

## 8. SEO & Accessibility Requirements
1. Page title: “Home Improvement Specialists | The Loft”
2. Meta description: 150-160 chars summarising services.
3. h1 used once (hero headline); subsequent sections use h2/h3 hierarchy.
4. All images include descriptive `alt` text.
5. Keyboard-navigable accordion, buttons, and form fields.

---

## 9. Acceptance Criteria (Implementation-Ready)
- All components implemented per spec IDs with test-IDs for QA automation.
- Lighthouse performance score ≥ 90 on desktop & mobile.
- Form submission returns `202` with `submissionId` echoed in UI.
- WCAG 2.2 AA compliance verified.

---

## 10. Open Questions / Next Steps
1. Confirm brand palette & typography with design team.  
2. Provide high-res imagery assets.  
3. Backend endpoint specification for `/api/contact` (Foundation Layer).  

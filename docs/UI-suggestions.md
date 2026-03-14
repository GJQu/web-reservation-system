# UI improvement suggestions

This doc lists optional enhancements beyond the current implementation. Use as a backlog for future iterations.

## Accessibility

- **Focus visible**: Already improved with `:focus-visible` in CSS. Consider a high-contrast theme toggle for users who need it.
- **Live regions**: For dynamic actions (e.g. cancel reservation), consider `aria-live` regions so screen readers announce success/error without a full page change.
- **Error summaries**: On validation errors, add an `aria-describedby` summary at the top of forms linking to invalid fields.

## Visual design

- **Dark/light mode**: Add a theme toggle and persist preference in `localStorage`; use CSS variables (already in place) to swap tokens.
- **Loading states**: Show a spinner or skeleton when fetching class list or reservations (e.g. if you add client-side JS or HTMX).
- **Empty gallery**: If `images` is empty, show a friendly “No images yet” message instead of an empty grid.
- **About page**: Add a hero image or simple illustration; break long paragraphs with subheadings or a timeline.

## Interaction

- **Confirm before cancel**: Implemented with `confirm()`. For a better UX, use a Bootstrap modal or a dedicated “Are you sure?” page.
- **Success feedback**: After making a reservation, consider a short success animation or a checkmark before redirecting.
- **Form validation**: Add client-side validation (e.g. required fields, password match) with HTML5 and/or minimal JS to reduce server round-trips.

## Responsiveness & performance

- **Images**: Use responsive images (`srcset`/`sizes`) and lazy loading for gallery and carousel to improve load time on mobile.
- **Touch**: Ensure buttons and links have a minimum touch target (~44px) on small screens; current Bootstrap classes generally comply.
- **Carousel**: On very small viewports, consider limiting carousel height so content below is visible without scrolling past a large image.

## Consistency

- **Page titles**: All pages now use “Page title · WPY Studio” in the layout.
- **Buttons**: Use `btn-primary` for primary actions and `btn-outline-*` for secondary (e.g. Cancel) consistently across the app.
- **Cards**: Use the same card style (e.g. `.card` with `.card-body`) for all content blocks so the UI feels cohesive.

## Future tech

- **HTMX or Alpine.js**: Add partial updates (e.g. refresh “Your reservations” without full reload) with minimal JS.
- **Progressive Web App**: Add a manifest and service worker for “Add to home screen” and offline fallback.
- **i18n**: If the studio serves multiple languages, add Flask-Babel and use keys in templates instead of hardcoded strings.

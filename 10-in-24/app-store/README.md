# 10 in 24 — App Store promotional images (promoted In-App Purchases)

These resolve the **Guideline 2.3.2** rejection (review June 10, 2026): the
promotional images for the promoted IAPs were the same as the app icon and were
duplicated across products.

## Files

| File | Use for promoted product | Motif |
|------|---------------------------|-------|
| `promo-monthly-1024.png` | **Monthly** subscription | Horizontal 24-hour duty/rest timeline |
| `promo-annual-1024.png`  | **Annual** subscription  | 12-month log-card grid + "Best Value" |

Each image is **1024 × 1024 px, RGB PNG, flattened (no alpha / transparency)**,
which meets Apple's promotional-image spec. Do **not** add rounded corners —
the App Store applies the corner mask automatically.

## Why these pass review

- **Different from the app icon** — the icon is a clock-tick ring with the
  "10 In 24" numerals inside a circular arrow. Neither image uses a clock face,
  a ring, the circular arrow, or numerals-in-a-circle. They use distinct
  illustrations (a flat timeline / a card grid) plus a small wordmark.
- **Unique per product** — Monthly uses a cool-blue horizontal timeline;
  Annual uses an amber-accented 12-card grid with a "BEST VALUE" badge.
  No two promoted products share an image.
- **Accurate** — each visualizes what the subscription delivers: Part 135
  flight-time and rest-period tracking (the 10-hours-in-24 requirement).

## Uploading

In App Store Connect → your app → **Monetization → In-App Purchases**, open each
promoted product, scroll to **Promoted In-App Purchase → Promotional Image**, and
upload the matching file. Save, then add/resubmit for review.

## Regenerating / editing

```bash
pip install Pillow
python3 generate_promo.py   # writes both PNGs next to the script
```

Brand color is `#316FB7`. Edit `generate_promo.py` to adjust copy, colors, or
layout; it renders at 3× and downsamples for crisp anti-aliased edges.

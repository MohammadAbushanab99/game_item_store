# Sample import files

Ready-to-use sample files that add **5 Egypt game items** through the admin import feature.

- `egypt_games.csv` — CSV version
- `egypt_games.xlsx` — Excel version (same data)

Both contain the required columns: `id, title, description, price, country`.

| id | title | price | country |
|----|-------|-------|---------|
| 200 | Scarab Amulet | 80.00 | EGY |
| 201 | Pharaoh's Staff | 220.00 | EGY |
| 202 | Nile Bow | 95.50 | EGY |
| 203 | Anubis Mask | 140.00 | EGY |
| 204 | Sphinx Riddle Scroll | 60.00 | EGY |

## How to import (2 steps)

The import only accepts countries that already exist, so add Egypt first.

1. Sign in as **admin** (`admin` / `Admin@12345`) and open the **Admin** page (`/admin`).
2. Under **Countries**, add: **Code** = `EGY`, **Name** = `Egypt` → *Add country*.
3. Under **Import games from a file**, choose `egypt_games.csv` (or `.xlsx`) → *Import*.
4. You should see **"Imported 5 product(s)."** Filter the product list by **Egypt** to see them.

> If you re-import the same file, it will be rejected because ids 200–204 already exist —
> that is the duplicate protection working. Change the ids to import again.

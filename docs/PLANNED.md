# Planned features

Feature ideas that are decided but not scheduled. The decision log (`decisions.md`) has a short entry for each one and points here for detail. Move an item out of this file (and update its decision entry) when it is built or dropped.

## Account groups

Decision entry: D-020. Not part of the MVP (D-001).

**Idea:** a user can follow many chess.com accounts (for example, 50 favorite GMs) and sort them into named groups, such as "good at endgames" and "good at gambits", to get insight from a group's combined games.

**Sketch (not final):**
- `account_groups`: `id`, `user_id`, `name`. A group belongs to one user.
- `account_group_members`: `(group_id, chess_account_id)`, composite primary key. Many-to-many, so one account can be in several groups.
- Members must be accounts the user already follows, so a group can only contain `user_chess_accounts` rows for that user (a composite foreign key to `(user_id, chess_account_id)` would enforce it).
- Group stats are the existing aggregates run over a set of accounts instead of one, matched through `game_players.player_uuid` (D-018).

**Open questions:**
- How a group's games are synced and how long that takes, given the soft limits (D-019) and chess.com rate limits.
- Whether a group's aggregates are computed on demand or cached.

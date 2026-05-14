# Dewey Databases

Dewey stores data using SQLite3 or MySQL. SQLite3 definitely works 100% (serious). Don't know if MySQL works that well but it should work too. I hope it does. I worked hard on it.

# Structures

One Dewey database has several tables, and their contents are as follows:

## Gacha Table(s)

### "gacha"
| Contains every user-made gacha card and information about them

| Name | Type | Use |
|------|------|-----|
|maker_id          |BIGINT      |Discord UID of who made the card|
|request_message_id|BIGINT      |Discord message ID of the approval embed (for buttons)|
|id                |BIGINT      |ID of card|
|accepted          |BOOL        |Whether the card was accepted or not|
|name              |varchar(256)|Name of the card|
|description       |varchar(256)|Description of the card|
|rarity            |varchar(256)|Rarity of the card (Common, Uncommon, Rare, Epic, Legendary)|
|filename          |varchar(256)|Name of the image file on disk|


### "gacha_user"
| Has cooldowns for users

| Name | Type | Use |
|------|------|-----|
|user_id    |BIGINT      |Discord UID|
|last_use   |BIGINT      |Unix Timestamp of last use|


### "gacha_cards"
| Inventory, everyone's inventory 

| Name | Type | Use |
|------|------|-----|
|id          |BIGINT      |ID of specific card "Inventory ID"|
|card_id     |BIGINT      |Gacha card ID|
|user_id     |BIGINT      |Discord UID of owner |


## DeweyCoins Table(s)

### "deweycoins"
| Contains every user and their balance and statistics

| Name | Type | Use |
|------|------|-----|
|uid            |BIGINT      |Discord user ID|
|balance        |BIGINT      |The user's balance|
|highestbalance |BIGINT      |- Statistic - The highest balance a user ever had|
|transactions   |BIGINT      |- Statistic - How many transactions that the user made|
|spent          |BIGINT      |- Statistic - How much a user spent in total|
|totalearned    |BIGINT      |- Statistic - How much a user earned in total|
|lostgambling   |BIGINT      |- Statistic - How much a user lost while gambling|
|gainedgambling |BIGINT      |- Statistic - How much a user profited while gambling|
|heads          |BIGINT      |- Statistic - How many heads a user had|
|tails          |BIGINT      |- Statistic - How many tails a user had|


## Reminders Table(s)

### "remindme"
| contains users and reminder times

| Name | Type | Use |
|------|------|-----|
|uid           |BIGINT      |Discord user ID|
|made          |BIGINT      |Unix time, when was made|
|whenr         |BIGINT      |Unix time, when to ring (ends with r because when is an sql keyword)|
|note          |varchar(256)|Note|
|guild         |BIGINT      |guild of the message id|
|channel       |BIGINT      |channel of the message id|
|message       |BIGINT      |message id sent when reminder set|


## User Settings Table(s)

### "settings"
| Settings for users

| Name | Type | Use |
|------|------|-----|
|uid              |BIGINT      |Discord user ID|
|roll_reminder_dm |bool        |Reminder to roll setting|
|roll_auto_sell   |bool        |Setting to auto sell|


## Dewey Settings Table(s)

### "permissions"
| Dewey Permissions

| Name | Type | Use |
|------|------|-----|
|id               |BIGINT      |Discord Snowflake|
|type             |BIGINT      |1 for role, 2 for member|
|permission       |BIGINT      |1 for admin type (permission override), 2 for GFAD disallowed role, 3 for dewey repeat users, may be appended later, 4 for card approver|
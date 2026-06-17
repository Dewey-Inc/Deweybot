import discord, math, Bot
import gachalib.views.browserow

import gachalib
import gachalib.types, gachalib.cards_inventory, gachalib.cards
import gachalib.views.card


#########################
#     Unnaccepted UI    #
#########################

class AdminSelect(discord.ui.Select):
    def __init__(self, page: int, card_id) -> None:
        self.page = page
        self.card_id = card_id
        options = [
            discord.SelectOption(label="Deny"),
            discord.SelectOption(label="Common"),
            discord.SelectOption(label="Uncommon"),
            discord.SelectOption(label="Rare"),
            discord.SelectOption(label="Epic"),
            discord.SelectOption(label="Legendary")
        ]
        super().__init__(placeholder="Rarity",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Deny":
            await gachalib.cards.approve_card(False, gachalib.cards.get_card_by_id(self.card_id)[1])
        else:
            gachalib.cards.update_card(self.card_id, "rarity", self.values[0])
            await gachalib.cards.approve_card(True, gachalib.cards.get_card_by_id(self.card_id)[1])
        layout = UnacceptedView(self.page)
        await interaction.response.edit_message(
            view=layout,
            allowed_mentions=discord.AllowedMentions(users=False)
        )











class UnacceptedView(discord.ui.LayoutView):
    def __init__(self, page: int=1):
        super().__init__(timeout=None)
        per_page = 4
        self.images: list[str] = []
        cards = gachalib.cards.get_unapproved_cards()[1]
        num_pages = math.ceil(len(cards) / per_page)
        cards_page = cards[(page-1)*per_page:page*per_page]

        items = [
            discord.ui.TextDisplay("## Unapproved cards"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(f"Page {page}/{num_pages}"),
            discord.ui.Separator(),
        ]
        for card in cards_page:
            image = f"{Bot.DeweyConfig["imageurl"]}/small/{gachalib.get_small_filename(card)}"
            self.images.append(image)
            items.append(discord.ui.Section(
                f"### {card.name}",
                f"{card.description}",
                f"-# ID: {card.card_id} by: <@{card.maker_id}>",
                accessory=discord.ui.Thumbnail(image)
            ))
            items.append(discord.ui.ActionRow(AdminSelect(page, card.card_id)))
            items.append(discord.ui.Separator())
        if num_pages > 1:
            browse_row = gachalib.views.browserow.BrowseRow(UnacceptedView, page, num_pages)
            if type(browse_row.children[0]) == discord.ui.Button and type(browse_row.children[1]) == discord.ui.Button:
                browse_row.children[0].disabled = page == 1
                browse_row.children[1].disabled = page == num_pages
            items.append(browse_row)

        container = discord.ui.Container(*items)
        self.add_item(container)











#########################
#      Inventory UI     #
#########################

class SortSelect(discord.ui.Select):
    def __init__(self, user: discord.User | discord.Member,  sort: str, button: bool) -> None:
        self.user = user
        self.button = button
        options = [
            discord.SelectOption(label="Rarity (ascending)"),
            discord.SelectOption(label="Rarity (descending)"),
            discord.SelectOption(label="Quantity (ascending)"),
            discord.SelectOption(label="Quantity (descending)"),
            discord.SelectOption(label="ID (ascending)"),
            discord.SelectOption(label="ID (descending)"),
        ]
        super().__init__(placeholder=sort,max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        layout = InventoryView(self.user, self.values[0], self.button, 1)
        await interaction.response.edit_message(view=layout)

class viewCardButton(discord.ui.Button):
    def __init__(self, card: gachalib.types.Card) -> None:
        super().__init__(label="View", style=discord.ButtonStyle.secondary)
        self.card = card

    async def callback(self, interaction: discord.Interaction) -> None:
        image=gachalib.get_small_thumbnail(self.card)
        await interaction.response.send_message(
            view=gachalib.views.card.GachaView(self.card, image), file=image, ephemeral=True,
            allowed_mentions=discord.AllowedMentions(users=False)
        )

class InventoryView(discord.ui.LayoutView):
    def __init__(self, user: discord.User | discord.Member, sort: str="Rarity (descending)", button: bool=True, page: int=1,):
        super().__init__(timeout=None)
        per_page = 5 - button
        self.images: list[str] = []

        cards = gachalib.cards_inventory.get_users_cards(user.id)[1]
        cards_grouped = gachalib.cards.group_like_cards(cards)
        num_pages = math.ceil(len(cards_grouped) / per_page)

        if "Rarity" in sort:
            cards_grouped = sorted(cards_grouped, key=lambda b: gachalib.rarity_order[gachalib.cards.get_card_by_id(card_id=b[0].card_id)[1].rarity])
        elif "Quantity" in sort:
            cards_grouped = sorted(cards_grouped, key=lambda b: b[1])
        else:
            cards_grouped = sorted(cards_grouped, key=lambda b: b[0].card_id)

        if "descending" in sort:
            cards_grouped.reverse()

        cards_page: list[tuple[gachalib.types.Card, int]] = cards_grouped[(page-1)*per_page:page*per_page]

        items = [
            discord.ui.TextDisplay("## Inventory Bowser!"),
            discord.ui.Separator(),
            discord.ui.ActionRow(SortSelect(user, sort, button)),
            discord.ui.TextDisplay(f"Page {page}/{num_pages}"),
            discord.ui.Separator(),
        ]
        for card in cards_page:
            image = f"{Bot.DeweyConfig["imageurl"]}/small/{gachalib.get_small_filename(card[0])}"
            self.images.append(image)
            items.append(discord.ui.Section(
                f"### {card[1]} × {card[0].name}",
                f"({card[0].rarity})\n"
                f"-# ID: {card[0].card_id}",
                accessory=discord.ui.Thumbnail(image)
            ))
            items.append(discord.ui.ActionRow(viewCardButton(card[0]))) if button else None
            items.append(discord.ui.Separator())
        if num_pages > 1:
            browse_row = gachalib.views.browserow.BrowseRow(InventoryView, page, num_pages, user, sort, button)
            if type(browse_row.children[0]) == discord.ui.Button and type(browse_row.children[1]) == discord.ui.Button:
                browse_row.children[0].disabled = page == 1
                browse_row.children[1].disabled = page == num_pages
            items.append(browse_row)

        container = discord.ui.Container(*items)
        self.add_item(container)









class BrowserView(discord.ui.View):
    def __init__(self,inventory:bool=False,uid:int=0,cards:list[gachalib.types.Card]=[],page:int=1,sort:gachalib.SortOptions="ID"):
        super().__init__(timeout=None)
        self.message = None
        self.page = page

        self.isInventory = inventory
        self.uid = uid
        
        if len(cards) == 0:
            if self.isInventory:
                _, self.cards = gachalib.cards_inventory.get_users_cards(self.uid)
                if sort == "ID":
                    self.cards = gachalib.cards_inventory.sort_cards_by_id(self.cards)
                elif sort == "Rarity":
                    self.cards = gachalib.cards_inventory.sort_cards_by_rarity(self.cards)
            else:
                _, self.cards = gachalib.cards.get_cards()
        else:
            self.cards = cards
    
    def getPage(self):
        return gachalib.cardBrowserEmbed(uid=self.uid,cards=self.cards,page=self.page,inventory=self.isInventory)


    async def updatePage(self,interaction:discord.Interaction):
        embed = self.getPage()

        if type(embed) == discord.Embed:
            await interaction.response.edit_message(content="", embed=embed, view=self)
        else:
            await interaction.response.edit_message(content=embed, embed=None, view=self)

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary, row=0, custom_id="backbtn")
    async def back_call(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        if self.page <= 0 or self.page - 1 <= 0:
            button.disabled = True
        else:
            button.disabled = False
            self.page -= 1

        await self.updatePage(interaction)


    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary, row=0, custom_id="fwdbtn")
    async def forward_call(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.page += 1
        await self.updatePage(interaction)
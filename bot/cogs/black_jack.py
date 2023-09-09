from discord.ext import commands


class BlackJack(commands.Cog, name="BlackJack"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.card_api = "https://www.deckofcardsapi.com/api/deck/"
        self.blackjack_games = {}

    async def create_deck(self):
        async with self.client.session.get(
            f"{self.card_api}new/shuffle/?deck_count=5"
        ) as response:
            new_deck = await response.json()
            return new_deck["deck_id"]

    async def shuffle_deck(self, deck_id):
        async with self.client.session.get(
            f"{self.card_api}{deck_id}/shuffle/"
        ) as response:
            shuffle = await response.json()
            if shuffle["success"]:
                return 200

    async def draw_card(self, deck_id, count=1):
        async with self.client.session.get(
            f"{self.card_api}{deck_id}/draw/?={count}"
        ) as response:
            card = await response.json()
            return card["cards"]

    def calculate_hand_value(hand):
        values = {"KING": 10, "QUEEN": 10, "JACK": 10, "ACE": 11}
        total_value = 0
        num_aces = 0

        for card in hand:
            if card["value"] in values:
                total_value += values[card["value"]]
            else:
                total_value += int(card["value"])

            if card["value"] == "ACE":
                num_aces += 1

        while total_value > 21 and num_aces > 0:
            total_value -= 10
            num_aces -= 1

        return total_value

    @commands.command(name="blackjack", description="Start a game of blackjack")
    async def blackjack(self, ctx):
        print(self.blackjack_games)
        print("blackjack")
        deck_id = await self.create_deck()
        print(deck_id)

        shuffle_success = await self.shuffle_deck(deck_id)
        print(shuffle_success)

        player_hand = await self.draw_card(deck_id, 2)
        print(player_hand)
        dealer_hand = await self.draw_card(deck_id, 2)
        print(dealer_hand)

        self.blackjack_games[ctx.author.id] = {
            "deck_id": deck_id,
            "player_hand": player_hand,
            "dealer_hand": dealer_hand,
        }
        player_hand_value = self.calculate_hand_value(player_hand)
        dealer_upcard = dealer_hand[0]

        await ctx.send(
            f"Your hand: {', '.join([card['value'] for card in player_hand])} (Total: {player_hand_value})"
        )
        await ctx.send(f"Dealer's upcard: {dealer_upcard['value']}")


async def setup(client):
    await client.add_cog(BlackJack(client))

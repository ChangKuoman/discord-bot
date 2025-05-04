from datetime import datetime, timedelta
from discord import Embed

class General:
    async def send_basic_embed(self, ctx, msg):
        embed = Embed(description=msg, color=self.COLOR)
        await ctx.send(embed=embed)

    def create_id(self, id):
        self.db[id] = {
            "balance": 0,
            "inventory": {},
            "daily": {
                "last_claimed": "",
                "total_claimed": 0,
                "streak": 0
            }
        }

    def get_dates(self):
        # DATE = YYYY-MM-DD
        # DATETIME = YYYY-MM-DD HH-MM-SS
        today_datetime = datetime.now() - timedelta(hours=5)
        tomorrow_datetime = today_datetime + timedelta(days=1)
        tomorrow_date = datetime(tomorrow_datetime.year, tomorrow_datetime.month, tomorrow_datetime.day)
        time_til_tomorrow = tomorrow_date - today_datetime
        yesterday_datetime = today_datetime - timedelta(days=1)
        return (today_datetime, yesterday_datetime, time_til_tomorrow)

    def can_claim(self, today_datetime, last_date_claimed):
        # have not claimed today
        if last_date_claimed == "":
            return True
        last_date_claimed = datetime.strptime(last_date_claimed, '%Y-%m-%d %H:%M:%S.%f')
        if (last_date_claimed.day != today_datetime.day
            or last_date_claimed.month != today_datetime.month
            or last_date_claimed.year != today_datetime.year):
            return True
        return False

    def have_streak(self, yesterday_datetime, last_date_claimed):
        # last claimed == yesterday
        if last_date_claimed == "":
            return True
        last_date_claimed = datetime.strptime(last_date_claimed, '%Y-%m-%d %H:%M:%S.%f')
        if (last_date_claimed.day == yesterday_datetime.day
            and last_date_claimed.month == yesterday_datetime.month
            and last_date_claimed.year == yesterday_datetime.year):
            return True
        return False

    def pagination(self, pages, page, embed):
        embed.clear_fields()
        for object in pages[page]:
            description = ""
            for key, value in object.items():
                if key == "name":
                    continue
                description += f"{' '.join(key.split('_')).title()}: `{value}`\n"

        embed.add_field(
            name=f"{object['name']}",
            value=f"{description}",
            inline=False
        )
        embed.set_footer(text=f"Page {page + 1}/{len(pages)}")

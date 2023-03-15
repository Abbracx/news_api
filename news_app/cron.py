from django_cron import CronJobBase, Schedule
import requests
import aiohttp
import asyncio
import logging
from datetime import datetime
from news_app.models import HackerNews
import json
from django.contrib.auth.models import User

logger = logging.getLogger('__name__')


class NewsCronJob(CronJobBase):

    RUN_EVERY_MINS = 1  # every 5 min
    RETRY_AFTER_FAILURE_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'news_app.news_cron_job'    # a unique code

    actual_news_obj = []
    session = None

    def do(self):
        # hacker news endpoint that returns a list of news ids
        NEWS_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty'
        headers = {'user-agent': 'newsids/0.0.1'}

        response = requests.get(NEWS_URL, headers=headers).text.split(',')

        cleaned_news_Ids = list(
            map(lambda id: id.strip().split()[0], response))[1:]

        latest_100_data = list(reversed(cleaned_news_Ids))[:100]  # latest 100

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.perform_operation(latest_100_data))
        
        user = None
        try:
            user = User.objects.get(username="hackernews")
        except Exception as e:
            user = User.objects.create_user(
                username="hackernews",
                email="hackernews@email.com",
                password="hackernews1234"
            )

        for news in self.actual_news_obj:

            # print(f'''
            #       {news.get("id", None)}\n
            #       {str(news.get("by", None))}\n
            #       {str(news.get("descendants", None))}\n
            #       {str(news.get("score", None))}\n
            #       {str(news.get("time", None))}\n
            #       {str(news.get("kids", None))}\n
            #       {str(news.get("title", None))}\n
            #       {str(news.get("type", None))}\n
            #       {str(news.get("url", None))}\n
            #       ''')
            try:

                news = HackerNews(
                    news_id=str(news.get('id', '')),
                    by=str(news.get('by', '')),
                    descendants=str(news.get('descendants', '')),
                    score=str(news.get('score', '')),
                    time=str(news.get('time', '')),
                    kids=json.dumps(news.get('kids', None)),
                    title=str(news.get('title', '')),
                    type=str(news.get('type', '')),
                    url=str(news.get('url', '')),
                    owner=user
                    )
                    
                news.save()
            except Exception as e:
                logger.error(f'Cron Error - {datetime.now()} - {e.message}')

    # Get actual news items given thier ids
    @classmethod
    async def perform_operation(cls, data):

        actions = []

        if cls.session is None:
            cls.session = aiohttp.ClientSession()
        for news in data:
            NEWS_URL = f'https://hacker-news.firebaseio.com/v0/item/{str(news)}.json?print=pretty'
            actions.append(asyncio.ensure_future(
                cls.get_news(cls.session, NEWS_URL)))

        await asyncio.sleep(1)
        news_response = await asyncio.gather(*actions)
        cls.actual_news_obj.extend(news_response)
        if cls.session:
            await cls.session.close()

    @classmethod
    async def get_news(self, session, url):
        async with session.get(url) as res:
            news_data = await res.json()
            return news_data

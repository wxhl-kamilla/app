from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.news import News
from data.reqparse import parser


def abort_if_news_not_found(news_id):  # вместо @app.errorhandler(404)
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        # Функция abort генерирует HTTP-ошибку с нужным кодом и возвращает ответ в формате JSON
        abort(404, message=f"News {news_id} not found")


# Для каждого ресурса (единица информации в REST называется ресурсом: новости, пользователи и т. д.) создается
# два класса: для одного объекта и для списка объектов: здесь это NewsResource и NewsListResource соответственно.

class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})

    #     get и post - без аргументов.
    #     Доступ к данным, переданным в теле POST-запроса - парсинг аргументов (reqparse)


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in news]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = News(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            is_private=args['is_private']
        )
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})

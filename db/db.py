
import asyncpg
import json

db_conn = {
    "user":"bogdan",
    "password":"12345678",
    "host":"127.0.0.1",
    "port":"5432",
    "database": "opinionbot12"
}

#Подключение к бд
async def db_pool():
    global db
    db = await asyncpg.create_pool(**db_conn)
    print("База данных подключена")

# Данные строки снизу для меня дают добавление пользователя
async def add_users(user_id: int, name: str):
    values = """
        INSERT INTO users(id, first_name)
        VALUES($1, $2)
        ON CONFLICT (id) DO NOTHING
        RETURNING id
    """
    return await db.fetchval(values, user_id, name)

async def add_results(from_user_id : int, to_user_id : int, answers : list, sec_message: str):
    values = """
    INSERT INTO results(from_user_id, to_user_id, answers, sec_message)
    VALUES($1, $2, $3, $4)
    """
    await db.fetchval(values, from_user_id, to_user_id, json.dumps(answers), sec_message)

# #проверка истинности если взаимность будет, то вернет истинность, иначе ложб (exist-используется для проверки именно существования строк)
async def check_relation(user1: int, user2: int):
    values = """
        SELECT 
            EXISTS(
                SELECT 1 FROM results
                WHERE from_user_id = $1 AND to_user_id = $2
            ) AS a_to_b,
            EXISTS(
                SELECT 1 FROM results
                WHERE from_user_id = $2 AND to_user_id = $1
            ) AS b_to_a
    """
    conclude = await db.fetchrow(values, user1, user2)
    return conclude["a_to_b"] and conclude["b_to_a"]
 


#сбор данных для stats.py прямиком из таблицы результатов, используя COUNT(*)
async def get_results(user_id:int):
    values = """
        SELECT COUNT(*)
        FROM results
        WHERE to_user_id = $1
    """
    return await db.fetchval(values, user_id)

#сбор данных для stats.py оставленных мною мнений для пользователей
async def your_opinion(user_id:int):
    values = """
        SELECT COUNT(*)
        FROM results
        WHERE from_user_id = $1
    """
    return await db.fetchval(values, user_id)

# async def get_results2(user_id: str):
#     values = """
#         SELECT COUNT(*)
#         FROM results
#         WHERE to_user_id = $1
#     """
#     collect = await db.fetch(values, user_id)
    
#     results = []
#     for i in collect:
#         results.append({
#             "from_user_id": i["from_user_id"],
#             "answers": i["answers"],
#             "sec_message": i["sec_message"]
#         })
#     return results
    
    
import json

async def get_results2(user_id: int):
    values = """
        SELECT from_user_id, answers, sec_message
        FROM results
        WHERE to_user_id = $1
        ORDER BY from_user_id
    """
    rows = await db.fetch(values, user_id) 

    results = []
    for row in rows:
        # row["answers"] может быть None или строкой JSON, поэтому делаем безопасный парсинг
        raw_answers = row.get("answers")
        try:
            parsed_answers = json.loads(raw_answers) if raw_answers else {}
        except Exception:
            # если парсинг падает — сохраняем как пустой dict, но можно логировать
            parsed_answers = {}

        results.append({
            "from_user_id": row.get("from_user_id"),
            "answers": parsed_answers,
            "sec_message": row.get("sec_message") or ""
        })

    return results


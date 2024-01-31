from aiohttp import web

app = web.Application()

async def process_user_info(request):
    try:
        data = await request.json()
        username = data.get("UserName", "")
        password = data.get("PassWord", "")
        user_ip = data.get("UserIP", "")
        user_port = data.get("UserPort", "")

        # 在这里可以添加逻辑，比如展示信息或进行其他处理
        print(f"Received POST request with JSON data: {data}")
        print(f"UserName: {username}, PassWord: {password}, UserIP: {user_ip}, UserPort: {user_port}")

        return web.Response(text="Request processed successfully")
    except Exception as e:
        return web.Response(text=f"Error processing request: {str(e)}", status=500)

app.router.add_post('/process_user_info', process_user_info)

if __name__ == '__main__':
    web.run_app(app, port=8080)

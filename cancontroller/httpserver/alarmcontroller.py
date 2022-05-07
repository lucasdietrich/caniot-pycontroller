from aiohttp import web
import aiohttp_jinja2


@aiohttp_jinja2.template("dashboard.view.j2")
async def handle_get(request: web.Request):
    form = await request.post()


    return {

    }
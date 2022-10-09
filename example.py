#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging

from datetime import datetime, timedelta
from enedisgatewaypy import EnedisByPDL, EnedisException

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Please , fill good values...
PDL = "0123456789"
TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


async def main():

    api = EnedisByPDL(pdl=PDL, token=TOKEN)

    try:
        start = (datetime.now() - timedelta(days=7))
        end = datetime.now()
        datas = await api.async_fetch_datas("consumption", start, end, PDL)
        # datas = await api.async_fetch_datas("consumption_load_curve", start, end)
        # datas = await api.async_get_contract()
        # datas = await api.async_get_addresses()
        logger.info(datas)
    except EnedisException as error:
        logger.error(error)

    await api.async_close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

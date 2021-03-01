#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.cmdline import execute


execute("scrapy crawl TeamSpider -s JOBDIR=jobs".split())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.cmdline import execute


execute("scrapy crawl GameIndexSpider -s JOBDIR=jobs".split())

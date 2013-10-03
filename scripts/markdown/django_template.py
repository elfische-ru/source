#!/usr/bin/env python3

from django import template

from django.conf import settings as settings
settings.configure()


def get_template(template_path):
    return template.Template(open(template_path).read())

def context(data):
    return template.Context(data, autoescape=False)

def render(template_path, data={}):
    return get_template(template_path).render(context(data))

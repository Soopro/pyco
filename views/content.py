#coding=utf-8
from __future__ import absolute_import

from flask import current_app, request, abort, render_template, redirect
import os

from helpers import (make_content_response,
                     helper_make_dotted_dict,
                     helper_process_url)

from .base import BaseView


class ContentView(BaseView):
    def get(self, _):
        # init
        config = self.config
        status_code = 200
        is_not_found = False
        run_hook = self.run_hook

        #for pass intor hook
        file = {"path": None}
        file_content = {"content": None}

        # load
        self.load_metas()
        self.load_plugins(config.get("PLUGINS"))
        run_hook("plugins_loaded")

        current_app.debug = config.get("DEBUG")
        self.init_context()

        run_hook("config_loaded", config=self.config)

        base_url = config.get("BASE_URL")
        charset = config.get('CHARSET')

        redirect_to = {"url": None}
        run_hook("request_url", request=request, redirect_to=redirect_to)
        site_redirect_url = helper_process_url(redirect_to.get("url"),
                                               config.get("BASE_URL"))
        if site_redirect_url and request.url != site_redirect_url:
            return redirect(site_redirect_url, code=301)

        # redirect to index if it is restful app
        if current_app.restful and request.path.rstrip('/') != '':
            return redirect(base_url, code=301)

        file["path"] = self.get_file_path(request.path)
        # hook before load content
        run_hook("before_load_content", file=file)
        # if not found
        if file["path"] is None:
            is_not_found = True
            status_code = 404
            file["path"] = self.content_not_found_full_path
            if not self.check_file_exists(file["path"]):
                # without not found file
                abort(404)

        # read file content
        if is_not_found:
            run_hook("before_404_load_content", file=file)

        with open(file['path'], "r") as f:
            file_content['content'] = f.read().decode(charset)

        if is_not_found:
            run_hook("after_404_load_content", file=file, content=file_content)
        run_hook("after_load_content", file=file, content=file_content)

        # parse file content
        tmp_file_content = file_content["content"]
        meta_string, content_string = self.content_splitter(tmp_file_content)

        try:
            page_meta = self.parse_page_meta(meta_string)
        except Exception as e:
            e.current_file = file["path"]
            raise e

        page_meta = self.parse_file_attrs(page_meta,
                                          file["path"],
                                          content_string)

        redirect_to = {"url": None}

        run_hook("single_page_meta",
                 page_meta=page_meta,
                 redirect_to=redirect_to)

        c_type = str(page_meta.get('type'))
        if c_type.startswith('_') and not redirect_to["url"]:
            default_404_slug = self.config.get("DEFAULT_404_SLUG")
            redirect_to["url"] = os.path.join(base_url,
                                              default_404_slug)

        content_redirect_to = helper_process_url(redirect_to.get("url"),
                                                 base_url)
        if content_redirect_to and request.url != content_redirect_to:
            return redirect(redirect_to["url"], code=302)

        self.view_ctx["meta"] = page_meta

        page_content = dict()

        page_content['content'] = content_string
        run_hook("before_parse_content", content=page_content)

        page_content['content'] = self.parse_content(page_content['content'])
        run_hook("after_parse_content", content=page_content)

        self.view_ctx["content"] = page_content['content']

        # content
        pages = self.get_pages() if not current_app.restful else []
        self.view_ctx["pages"] = pages

        run_hook("get_pages",
                 pages=self.view_ctx["pages"],
                 current_page=self.view_ctx["meta"])
        # template
        template = dict()

        template['file'] = self.view_ctx["meta"].get("template")

        run_hook("before_render", var=self.view_ctx, template=template)

        template_file_path = self.theme_path_for(template['file'])
        template_file_absolute_path = self.theme_absolute_path_for(
                                                        template_file_path)

        if not os.path.isfile(template_file_absolute_path):
            template['file'] = None
            default_template = config.get('DEFAULT_TEMPLATE')
            if is_not_found:
                abort(404)
            else:
                template_file_path = self.theme_path_for(default_template)


        # make dotted able
        for k,v in self.view_ctx.iteritems():
            self.view_ctx[k] = helper_make_dotted_dict(v)

        output = {}
        output['content'] = render_template(template_file_path,
                                            **self.view_ctx)
        run_hook("after_render", output=output)
        return make_content_response(output['content'], status_code)

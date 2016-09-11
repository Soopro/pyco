# Pyco

## Concept

Pyco is a simple, not very fast, flat file CMS base on Python Flask. It is design to simulation our Could Content Service, will help developers make Themes from localhost.

Pyco build with plugin supported and custom able config settings, that mean is you can also host a website with own needs, but it is not design for large portal site, so please make sure is not very big traffic.

This project NEVER testing on Windows, if you are use windows only, We are sorry.

[Github Repo](http://github.com/soopro/pyco)

<br><br>

## Installation

1. Make sure you have `python 2.7` and `pip`.
2. Clone this github repo [http://github.com/soopro/pyco](http://github.com/soopro/pyco).
3. Make sure current branch is `master`.
4. Get the project root folder, run `pip install -r requirements.txt`. (you might need `sudo`).
5. Check all install result was succeed.
6. Done.


## Run

First, you have to enter the pyco folder obviously, then you can run pyco in multiple ways.

* `sh start.sh`: Run as backend. you will need `sh stop.sh` to stop it, or kill the system progress manually.

* `python pyco.py`: Run as develop.



## Documentation

### Config Settings

You can modify the `config.py` to change base settings.

*Those settings below is for simulate the cloud platform settings. please do not chagne it if you want use pyco to develop a cloud base theme.*

* `DEBUG`: **[ bool ]** Switch of debug mode. The debug mode will showing up some additional information and reload theme very request. you can also access from `current_app.debug`. Defualt is `True`.

* `HOST`: **[ str ]** Host local ip address. Default is `"0.0.0.0"`.

* `PORT`: **[ int ]** Host port. Default is `5500`.

* `THEME_NAME`: **[ str ]** Theme name slug. Default is `"default"`.

* `STATIC_PATH`: **[ str ]** Static base path of themes. Default is `"static"`.

* `BASE_URL`: **[ str ]** Site base url. Default is `"http://localhost:5500"`.

* `API_BASEURL`: **[ str ]** Site api baseurl for ajax request. Default is `"http://localhost:5500/restapi"`.

* `LIBS_URL`: **[ str ]** Site libs base url, all that common libs will host here. Default is `"http://libs.soopro.io"`.

* `THEME_URL`: **[ str ]** Theme url of Site. It is base on `BASE_URL/STATIC_PATH/THEME_NAME`.

* `UPLOADS_DIR`: **[ str ]** Uploads dir will be `"uploads"`.

* `CONTENT_DIR`: **[ str ]** Contents dir will be `"content"`.

* `PLUGIN_DIR`: **[ str ]** Plugin dir will be `"plugins"`.

* `THEMES_DIR`: **[ str ]** Themes dir will be `"themes"`.

* `LANGUAGES_DIR`: **[ str ]** The language dir in side each theme will be `"languages"`.

* `CHARSET`: **[ str ]** Site date files charset. Default is `"utf8"`.

* `CONTENT_FILE_EXT`: **[ str ]** content file ext will be `".md"`.

* `TEMPLATE_FILE_EXT`: **[ str ]** template file ext will be `".html"`.

* `SITE_DATA_FILE`: **[ str ]** Site date is general data of the site, Default is "site.json".

* `THEME_CONF_FILE`: **[ str ]** Theme config file is `"config.json"`.

* `DEFAULT_TEMPLATE`: **[ str ]** Default template name is `"index"`.

* `DEFAULT_DATE_FORMAT`: **[ str ]** Default input date format is `"%Y-%m-%d"`. This format will not effect while output Date format.

* `DEFAULT_EXCERPT_LENGTH`: **[ str ]** Excerpt length will be `162`.

* `DEFAULT_EXCERPT_ELLIPSIS`: **[ str ]** Excerpt ellipsis will be `"&hellip;"` aka `...`.

* `DEFAULT_INDEX_SLUG`: **[ str ]** Index page slug default as `"index"`.

* `DEFAULT_404_SLUG`: **[ str ]** 404 page slug default as `"error-404"`.

* `DEFAULT_SEARCH_SLUG`: **[ str ]** Search page slug default as `"search"`.

* `DEFAULT_TAXONOMY_SLUG`: **[ str ]** Taxonomy page slug. In fact there are many kind of taxonomy, but we only use `category` here. Default as `"category"`.

* `DEFAULT_TAG_SLUG`: **[ str ]** Tags page slug default as `"tag"`.

* `INVISIBLE_SLUGS`: **[ list ]** Define some content slug (lower case of file name) will not showing up in query list. Default is `[DEFAULT_INDEX_SLUG, DEFAULT_404_SLUG, DEFAULT_SEARCH_SLUG, DEFAULT_TAXONOMY_SLUG, DEFAULT_TAG_SLUG]`.

* `USE_MARKDOWN`: **[ bool ]** Use markdown for rendering or not. Default is `False`.

* `MARKDOWN_EXTENSIONS`: **[ list ]** Use markdown extensions if `USE_MARKDOWN` is opened. Remember you have to install by your self before use it, and it IS NOT a Plugin. default is `['gfm']`.

* `MAXIMUM_QUERY`: **[ int ]** A number of maximum returns of each content query method. A very large number could cost really slow rendering. Default is `60`.

* `DEFAULT_SEARCH_ATTRS`: **[ list ]** Define default search attributes, if given the attribute key is not exist in major fields, it will switch into `meta` to do the searching. Default is `['title']`.

* `SHORT_FIELD_KEYS`: **[ dict ]** Make short keyword for fields key. Default is: `{'type': 'content_type'}`

* `SORTABLE_FIELD_KEYS`: **[ list ]** Define which major fields in raw files data can be sorting. Default is `['priority', 'date', 'creation', 'updated']`.

* `STRUCTURE_FIELD_KEYS`: **[ list ]** Define content fileds which can be query, those keys will load as major fields for the raw files data, others will host in `meta` field in raw file data as custom fields, but remember all fields will reform after rendering. Default is `['slug', 'content_type', 'priority', 'parent', 'date', 'creation', 'updated', 'template', 'tags']`.

* `PLUGINS`: **[ list ]** all plugins packpage name here.


### Hooks of Plugin

Pyco supported plugins. Plugins use several hooked functions, and order by the request work flow. Some data could be customlize, you have to print out to understand attributes. Hooks such as:

1. `config_loaded(config)`: While site date, config, theme_meta loaded.
    * `config`: **[ dict ]** read-only. include `config settings`, `theme_meta` and `site_meta`.
    
2. `request_url(request)`: While the request is confirmed.
    * `request`: **[ dict ]** a flask request object.

3. `before_load_content(path)`: Before load the page.
    * `path`: **[ dict ]**
      1. `content_type`: **[ str ]** content type slug.
      2. `slug`: **[ str ]** file slug
      
4. `after_load_content(path, file)`: After content loaded.
    * `path`: **[ dict ]**
      1. `content_type`: **[ str ]** content type slug.
      2. `slug`: **[ str ]** file slug
    * `file`: **[ dict ]** a file dict. Print out to see all attributes.

5. `before_404_load_content(path)`: Before load the 404 page.
    * `path`: **[ dict ]**
      1. `content_type`: **[ str ]** content type slug.
      2. `slug`: **[ str ]** file slug

6. `after_404_load_content(path, file)`: After 404 page loaded.
    * `path`: **[ dict ]**
      1. `content_type`: **[ str ]** content type slug.
      2. `slug`: **[ str ]** file slug
    * `file`: **[ dict ]** a file dict. Print out to see all attributes.

7. `before_parse_content(content)`: Before parse the content.
    * `content`: **[ dict ]**
      1. `content`: raw content string.
      
8. `after_parse_content(content)`: After content parsed.
    * `content`: **[ dict ]**
      1. `content`: parsed content string.

9. `before_read_page_meta(headers)`: Before read page meta.
    * `headers`: **[ dict ]** Print out to see all attributes.

10. `after_read_page_meta(page_meta, redirect)`: After read page meta.
    * `page_meta`: **[ dict ]** All page readed attrbiutes.
    * `redirect`: **[ dict ]** or **[ None ]** redirect information. for rest api this param will be None, because there is no way to redirect.
      1. `url`: **[ str ]** redirect url, default is `None`.

11. `get_pages(pages, current_page_id)`: While query contents.
    * `pages`: all contents. Print out for attributes.

12. `before_render(var, template)`: Before render (not support restapi).
    * `var`: **[ dict ]** context for the rendering.
    * `template`: **[ dict ]** template information.
      1. `name`: **[ str ]** template name.
    
    
13. `after_render(rendered)`: After render (not support restapi).
    * `rendered`: **[ dict ]** rendered output.
      1. `output`: **[ str ]** the content return to browser.


**Attation**: Our cloud platform might not support your plugins modify.


### Manage Content

Pyco is flat file CMS, there is no database. All content host as `.md` markdown file in `content` folder. 

The type of contents is base on folder name. The files in the root of `content` folder is static page type, call `page`. Add other content types just create a folder then put `.md` inside, the folder name will be `slug` of this content type.

There is global content data for whole site is host in a json file in root of `content` folder, call `site.json`.

***DO NOT USE ANY NON ASCII CODE ON FILE NAME OR DIR NAME***

*the markdown parse support is turn of by default, you have you turn it on if you need, otherwise only support text/html.*

#### Site.json

Global content data for whole site. some data is simulation for cloud service, if you don't know what is it, leave it alone.

* `app_id`: **[ str ]** the app id, simulation an real `app_id`.

* `slug`: **[ str ]** site slug, simulation app slug. 

* `type`: **[ str ]** site type, simulation app type.

* `content_types`: **[ dict ]** content types is define by folder name, but those folder name is always a `slug`, given a Text title for content type here. `{"page": "Pages"}` etc,.

* `menus`: **[ dict ]** define multiple menus. Follow `menu` structure exactly.
  1. `< menu_slug >`: **[ list ]** a menu.
    * `slug`: **[ str ]** menu item slug.
    * `title`: **[ str ]** menu item title.
    * `link`: **[ str ]** menu link, system will generate `url` by `link`.
    * `target`: **[ str ]** menu link target, such as `_blank`, `_self`.
    * `related_type`: **[ str ]** menu item related content type slug.
    * `meta`: **[ dict ]** menu item meta, put custom data as you wish.
    * `nodes`: **[ list ]** children menu items

* `taxonomies`: **[ dict ]** All taxonomy host here.
  * `< taxonomy_slug >`:
    1. `title`: **[ str ]** Taxonomy title.
    2. `content_types`: **[ list ]** list of supported content types.
    3. `terms`: **[ list ]** terms of this taxonomy.
      1. `key`: **[ str ]** term key.
      2. `title`: **[ str ]** term title.
      3. `class`: **[ str ]** term sytle class.
      4. `meta`: **[ dict ]** term data in meta. leave it empty if you don really need it.
        * `pic`: **[ str ]** pic for term display.
      5 `nodes`: **[ list ]** children terms here.

* `meta`: Site meta
  * `title`: **[ str ]** site title, aka app title.
  * `logo`: **[ str ]** media src of logo.
  * `favicon`: **[ str ]** media src of favicon.
  * `bg`: **[ dict ]** media dict of site level background.
  * `contact`: **[ str ]** contact info.
  * `copyright`: **[ str ]** copyright.
  * `description`: **[ str ]** description text.
  * `license`: **[ str ]** license.
  * `locale`: **[ str ]** language locale.
  * `seo`: **[ str ]** seo codes here.
  * `analytics`: **[ str ]** third part analytic codes here.
  * `socials`: **[ dict/list ]** social medias if you need.
    ```json
    {
      "facebook":{"name":"Facebook","url":"#","code":"facebook"},
      "twitter":{"name":"Twitter","url":"#","code":"twitter"}
    }
    ```
  * `translates`: **[ dict ]** translates if you need.
    ```json
    {
       "zh_CN":{"name":"汉语","url":"http://....."},
       "en_US":{"name":"English","url":"http://....."}
    }
    ```


***Example***
```json
{
  "app_id": "pyco_app_id",
  "slug": "pyco",
  "type": "ws",
  "content_types": {
    "post": "Posts",
    "page": "Pages"
  },
  "menus": {
    "primary": [
      {
        "key": "home",
        "meta": {},
        "nodes": [],
        "title": "Home",
        "link": "/"
      },
      {
        "key": "page",
        "meta": {},
        "nodes": [],
        "title": "Static Page",
        "link": "/page"
      }
    ]
  },
  "taxonomies": {
    "category": {
      "title": "Category",
      "content_types": ["post"],
      "terms": [
        {"slug": "food", "title": "Food", 
         "meta": {"pic": "","parent": ""}, "priority": 0},
        {"slug": "book", "title": "Book",
         "meta": {"pic": "","parent": ""}, "priority": 0}
      ]
    }
  },
  "meta": {
    "locale": "en_US",
    "favicon": "",
    "logo": "",
    "bg": "",
    "contact": "<a href='mailto:redy@imredy.com'>redy@imredy.com</a>",
    "copyright": "2015 Made by Pyco.",
    "description": "...",
    "license": "MIT",
    "title": "Sample",
    "socials":{
      "facebook": {"name": "Facebook", "url": "#", "code": "facebook"},
      "twitter": {"name": "Twitter", "url": "#", "code": "twitter"}
    },
    "translates": {
      "en_US": {"name": "English", "url": "#" },
      "zh_CN": {"name": "中文", "url": "#" }
    }
  }
}

```


#### Single Content File

All Content is host by `.md` file put in `content` folder.
Use folder to define different `content types`. (folder and file name could be latin, dash `-`, underscore `_` or number)

The default content type is `page`, every `.md` in root of `content` folder is `page`, that's why don't have a folder named it.

Each content file `.md`, separated with 2 parts, `meta` and `content`.

Pyco also support `shortcode`. `shortcode` is for generation dynamic value in your contents, must exactly follow this format `[%shortcode%]`. if you really want a str like that, you can use html entity to replace the `%` to `&#37;`. You have to quote it while using in `meta`, such as `'[%shortcode%]/your_pic.jpg'` because that's YAML. 

* `[%uploads%]`: A shortcode for uploads url.

* `[%theme%]`: A shortcode for theme url, same as above.


##### Meta

Multiple line between `/* ... */` is meta. you can define attribute whatever you want. It's YAML format. google it to learn YAML format.


Some attribute will be reserved:

* `date`: **[ str ]** Input date format with yyyy-mm-dd.
* `priority`: **[ int ]** Priority of content, the smaller the front, default is `0`.
* `parent`: **[ str ]** Parent content slug, default is empty str.
* `taxonomy`: **[ dict ]** host term's slug of all supported taxonomies, such as 'cateogry: sample-term'.
* `tags`: **[ list ]** A list of str for tags.
* `redirect`: **[ str ]** Redirect url.
* `template`: **[ str ]** Template name.
* `status`: **[ int ]** Publish status, `1` - published, `0` - draft, default is published.


*In the .md file, the attributes's first letter is capitalized, it just for good looking, will automatice lowercase after the file is loaded.*

##### Content

After `/* ... */` is Content, must be simple HTML with inline styles or markdown format (make sure markdown parse is turn on in config settings). Complex html with layout styles and classes is NOT recommend, those content will very difficult to maintain after sync to cloud service. Any complex content you might have to depend on theme's layout design.


***Example***
```markdown
/*
Date: '2014-01-01'
Priority: 0
Status: 1
Taxonomy:
   category: sample-term
Template: page
Title: Static Page
Featured_img:
  src: '[%uploads%]/cover_img.png'
  title: 'cover image'
*/
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo  ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis   dis parturient montes, nascetur ridiculus mus.</p>

<p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores consequatur aut perferendis doloribus asperiores repellat.</p>

```

### Themes

You can create own themes for pyco with Jinja2 template language.
After your got a new theme, put intro themes folder and change settings in `config.py` to activated your owen theme.

Learn Jinja2 from here [Jinja2 Docs](http://jinja.pocoo.org/docs/dev/templates)


#### Template context

Learn more about template context.

[Go this repo](https://github.com/Soopro/rafiki/)

https://github.com/Soopro/rafiki/blob/master/jinja2_template.md

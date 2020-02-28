# Pyco

## Concept

Pyco is a simple, not very fast, flat file CMS base on Python Flask. It is design to simulation our Could Content Service, will help developers make Themes from localhost.

Pyco build with plugin supported and custom able config settings, that mean is you can also host a website with own needs, but it is not design for large portal site, so please make sure is not very big traffic.

This project NEVER testing on Windows, if you are use windows only, We are sorry.

[Github Repo](http://github.com/soopro/pyco)

<br><br>

## Installation

1. Make sure you have `python 3.7` or later and `pip`.
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

* `THEMES_DIR`: **[ str ]** Themes dir will be `"themes"`.
* `THEME_NAME`: **[ str ]** Theme name slug. Default is `"default"`.

* `UPLOADS_DIR`: **[ str ]** Uploads dir will be `"uploads"`.
* `BACKUPS_DIR`: **[ str ]** Backups dir will be `"backups"`.
* `PLUGINS_DIR`: **[ str ]** Plugin dir will be `"plugins"`.

* `BASE_URL`: **[ str ]** Site base url. Default is `"http://localhost:5500"`.

* `API_URL`: **[ str ]** Site api baseurl for ajax request. Default is `"http://localhost:5500/restapi"`.

* `THEME_URL`: **[ str ]** Theme url of Site. It is base on `BASE_URL/STATIC_PATH/THEME_NAME`.

* `UPLOADS_URL`: **[ str ]** uploads url of Site. default is `BASE_URL/UPLOADS_DIR`.

* `RES_URL`: **[ str ]** res url of Site. default is `UPLOADS_URL/res`. Change it to online url if you need.

* `PLUGINS`: **[ list ]** all plugins packpage name here.


### Hooks of Plugin

Pyco supported plugins. Plugins use several hooked functions, and order by the request work flow. Some data could be customlize, you have to print out to understand attributes. Hooks such as:

1. `config_loaded(config)`: While config, site date, theme_meta loaded.
    * `config`: **[ dict ]** read-only. include `config`, `theme_meta` and `site_meta`.

2. `request_url(request)`: While the request is confirmed.
    * `request`: **[ dict ]** a flask request object.

3. `get_page_content(content)`: After content parsed.
    * `content`: **[ dict ]**
      1. `content`: parsed content string.

4. `get_page_meta(page_meta, redirect)`: After read page meta.
    * `page_meta`: **[ dict ]** All page readed attrbiutes.
    * `redirect`: **[ dict ]** or **[ None ]** redirect information. for rest api this param will be None, because there is no way to redirect.
      1. `url`: **[ str ]** redirect url, default is `None`.

5. `get_pages(pages, current_page_id)`: While query contents.
    * `pages`: all contents. Print out for attributes.

6. `before_render(context, template)`: Before render (not support restapi).
    * `context`: **[ dict ]** context for the rendering.
    * `template`: **[ dict ]** template information.
      1. `name`: **[ str ]** template name.


7. `after_render(rendered)`: After render (not support restapi).
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

* `app_id`: **[ str ]** simulation an `app_id` (could be encrypted).

* `slug`: **[ str ]** site slug, simulation app slug.

* `type`: **[ str ]** site type, simulation app type.

* `content_types`: **[ dict ]** content types is define by folder name, but those folder name is always a `slug`, given a Text title for content type here. `{"page": "Pages"}` etc.

* `menus`: **[ dict ]** define multiple menus. Follow `menu` structure exactly.
  1. `< menu_slug >`: **[ list ]** a menu.
    * `slug`: **[ str ]** menu item slug.
    * `title`: **[ str ]** menu item title.
    * `link`: **[ str ]** menu link, system will generate `url` by `link`.
    * `target`: **[ str ]** menu link target, such as `_blank`, `_self`.
    * `related_type`: **[ str ]** menu item related content type slug.
    * `meta`: **[ dict ]** menu item meta, put custom data as you wish.
    * `nodes`: **[ list:dict ]** children menu items

* `categories`: **[ dict ]** All categories host here.
  1. `name`: **[ str ]** Category name.
  2. `content_types`: **[ list ]** list of supported content types.
  3. `terms`: **[ list:dict ]** terms of this category.
    1. `key`: **[ str ]** term key.
    2. `name`: **[ str ]** term name.
    4. `meta`: **[ dict ]** term data in meta. leave it empty if you don really need it.
      * `class`: **[ str ]** term sytle class.
      * `pic`: **[ str ]** pic for term display.
    5 `parent`: **[ str ]** mark parent term key.

* `slots`: **[ dict ]** All widget slots host here.
  * `< slot_key >`:
    1. `name`: **[ str ]** slot label.
    2. `src`: **[ str ]** slot media src.
    3. `route`: **[ str ]** slot route.
    4. `scripts`: **[ str ]** slot scripts.
    5. `data`: **[ dict ]** slot data key/value map.
    6. `status`: **[ str ]** slot on (1) or off (1).

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
  * `languages`: **[ list ]** languages switcher if you need.
    ```json
    [
       {"key": "zh_CN", "name":"汉语", "url":"http://....."},
       {"key": "en_US", "name":"English", "url":"http://....."}
    ]
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
  "categories": {
    "name": "Category",
    "content_types": ["post"],
    "terms": [
      {"key": "daily", "meta":{"name": "Daily"}},
      {"key": "food", "meta":{"name": "Food"}},
      {"key":"daily-2", "meta":{"name": "Daily"}, "parent":"daily"},
      {"key":"food-2", "meta":{"name": "Food"}, "parent":"food"}
    ]
  },
  "slots": {
    "event": {"script": "<div style='background:#ccc;max-width:200px;padding:16px;'>This is EVENT wdiget slot.</div>"}
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
    "socials":[
      {"key": "facebook", "name": "Facebook", "url": "#", "code": "facebook"},
      {"key": "twitter", "name": "Twitter", "url": "#", "code": "twitter"}
    ],
    "languages": [
       {"key": "zh_CN", "name":"汉语", "url":"http://....."},
       {"key": "en_US", "name":"English", "url":"http://....."}
    ]
  }
}

```


#### Single Content File

All Content is host by `.md` file put in `content` folder.
Use folder to define different `content types`. (folder and file name could be latin, dash `-`, underscore `_` or number)

The default content type is `page`, every `.md` in root of `content` folder is `page`, that's why don't have a folder named it.

Each content file `.md`, separated with 2 parts, `meta` and `content`.

Pyco also support `shortcode` for people who need write data file manually. `shortcode` will generation dynamic value in your data. BUT, shortcode is only work for manual operation. When you saved data in Admin Panel, those shortcode will be replace to what they should be.

Shortcode is a str as this format `[%<shortcode_name>%]`. if you really want a text exactly the same as shortcode, you must use html entity to replace the `%` to `&#37;`. Remember You have to **quote** it while using in `meta`, such as `'[%uploads%]/your_pic.jpg'` because YAML can not read `%`.


We provide one default shortcode:

* `[%uploads%]`: A shortcode for uploads url.

You can modify or add your shortcodes form config.py. but keep in your mind, too many shortcode always slow down data loading time.


##### Meta

Multiple line between `/* ... */` is meta. you can define attribute whatever you want. It's YAML format. google it to learn YAML format.


Some attribute will be reserved:

* `date`: **[ str ]** Input date format with yyyy-mm-dd.
* `priority`: **[ int ]** Priority of content, the smaller the front, default is `0`.
* `parent`: **[ str ]** Parent content slug, default is empty str.
* `terms`: **[ list:str ]** host term's key of category, such as `['term-key-1', 'term-key-2']`.
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
Terms:
- term-key-1
- term-key-2
- some-key
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

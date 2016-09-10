# Pyco

## Concept

Pyco is a stupidly simple, blazing fast, flat file CMS base on Python Flask.
Start a localhost with pyco help you build own `theme`.

Never testing on Windows, if you are use windows only, We are sorry.

[Github Repo](http://github.com/soopro/pyco)

<br><br>

## Installation

1. Make sure you have python and pip.
2. Clone this github repo [http://github.com/soopro/pyco](http://github.com/soopro/pyco).
3. Make sure current branch is `master`.
4. Get the project root folder, run `pip install -r requirements.txt`. (you might need `sudo`).
5. Check all install result was succeed.
6. Done.

## Run

First, you have to enter the pyco folder obviously, then you can run pyco in multiple ways.

* `sh start.sh`: Run as backend. you will need `sh stop.sh` to stop it, or kill the system progress manually.

* `python pyco.py`: Run as develop.



## Usage

### Config

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


### Themes

You can create own themes for pyco with Jinja2 template language.
After your got a new theme, put intro themes folder and change settings in `config.py` to activated your owen theme.

Learn Jinja2 from here [Jinja2 Docs](http://jinja.pocoo.org/docs/dev/templates)


### Plugins

Pyco supported plugins. We already provider several plugins, such as:

* `draft`: add `status` support in contents. when you want mark a content as draft, just set status to `0`. (`1` for publish)

* `languages`: add multi-languages support for pyco.

* `is`: add `is_front`, `is_404`, `is_current` support.

* `contect_types`: automatically processing content_types for content which don't have `type` attribute.
* `redirect`: process redirect for content.

* `template`: given a default `template` base on `type` for content which don't have template attribute.

* `marker`: parse content with short code marks.

* `jinja_helper`: add multiple helpers and filters, learn more from the ***jinja2 template*** document of our system. Check [this repo](http://github.com/soopro/rafiki)

**Attation**: If you want build themes for our system, you should not change any thing about plugins, because our system might not support your modify.


### Content

Pyco is flat file CMS, there is no database. All content host as `.md` markdown file in `content` folder.

The type of contents is base on folder name. The files in the root of `content` folder is static page call 'page'. Add other content types just create a folder then put `.md` inside, the folder name will be `slug` of this content type.

There is global content data for whole site call **Site Meta**, to having this data, you have to put a `site.json` file in the root of `content` folder.


## Site.json

Global content data for whole site.

* `app_id`: **[ str ]** the app id, sometime you want work with an real `app_id`, you can put it here. If you don't know where to find an real `app_id`, leave it alone. default is `pyco_app`.

* `slug`: **[ str ]** site slug. aka app slug
* `type`: **[ str ]** site type. aka app type

* `content_types`: **[ dict ]** content types is define by folder name, but those folder name is always a `slug`, given a Text title for content type here.

* `menus`: **[ dict ]** define multiple menus. Follow `menu` structure exactly.
  1. `< menu_slug >`: **[ list ]** a menu.
    * `slug`: **[ str ]** menu item slug
    * `title`: **[ str ]** menu item title
    * `link`: **[ str ]** menu link, system will generate `url` by `link`.
    * `meta`: **[ dict ]** menu item meta, put custom data in side as you wish.
    * `nodes`: **[ list ]** children menu items

* `taxonomies`: **[ dict ]** All taxonomy host here. (also could be tax for short)
  * `< taxonomy_slug >`:
    1. `title`: **[ str ]** Taxonomy title.
    2. `content_types`: **[ list ]** list of supported content types.
    3. `terms`: **[ list ]** terms of this taxonomy.
      1. `key`: **[ str ]** term key
      2. `title`: **[ str ]** term title
      6. `meta`: **[ dict ]** term data in meta. leave it empty if you don really need it.
        * `pic`: **[ str ]** pic for term display.

* `meta`: Site meta
  * `title`: **[ str ]** site title. aka app title
  * `type`: **[ str ]** site type. aka app type
  * `logo`: **[dict]** media of logo
    * `src`: **[ str ]** media src.
    * `title`: **[ str ]** media title.
    * `link`: **[ str ]** media link if have one.
    * `target`: **[ str ]** target for media link. '\_blank' or something else.
    * `class`: **[ str ]** media class.

  * `contact`: **[ str ]** contact info.
  * `copyright`: **[ str ]** copyright.
  * `description`: **[ str ]** description text.
  * `license`: **[ str ]** license.
  * `locale`: **[ str ]** language locale.
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
  "slug":"pyco",
  "type":"ws",
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
  "meta": {
    "logo": {
      "src": "http://myuploads.com/logo.png",
      "title": "my logo",
      "link": "http://linkto.link",
      "target": "target for media link. '_blank' or something else.",
      "class": "logo"
    },
    "author": "redy",
    "copyright": "2015 Made by Pyco.",
    "description": "A simple example of Pyco side ...",
    "license": "MIT",
    "locale": "en_US",
    "title": "Pyco"
  },
  "taxonomies":{
    "category": {
      "title":"Category",
      "content_types": ["post"],
      "terms": [
        {"slug":"food","title":"Food","meta":{"pic":"","parent":""}, "priority": 0 },
        {"slug":"book","title":"Book","meta":{"pic":"","parent":""}, "priority": 0 }
      ]
    }
  }
}

```


## Single Content

All Content is host by `.md` file put in `content` folder.
Use folder to define different `content types`. (folder must be latin or number or - or _ )

The default content type is `page`, every `.md` in root of `content` folder is `page`, that's why don't have a folder named it.

In each `.md` separate `meta` and `content`.

* `meta`: Multiple line between `/* ... */` is meta. you can define attribute whatever you want. It's YAML format. learn YAML format by your self. please.

* `content`: After `/* ... */` is Content, must be simple HTML code here is recommend. which not recommend is use complex html with styles or classes, those content will very difficult to maintain after upload to our system. (better to use html just like markdown could do.) The complex content you have use theme to deal with not rich text contents.

* `shortcode`: shortcode is for generation dynamic value in your contents, it's follow this format `[%shortcode%]`. if you really want a str like that, you can use html entity to replace the `%` is `&#37;`

  1. `[%uploads%]`: A shortcode for uploads url, you have to quote it while using in `meta`, because that's YAML. ```[%uploads%]/your_pic.jpg```
  2. `[%theme%]`: A shortcode for theme url, same as above.


```markdown
/*
Date: '2014-01-01'
Priority: 0
Status: 1
Category: haha
Template: page
Title: Static Page
Featured_img:
  src: '[%uploads%]/cover_img.png'
  title: 'cover image'
*/
<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo  ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis   dis parturient montes, nascetur ridiculus mus.</p>

<p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores consequatur aut perferendis doloribus asperiores repellat.</p>

```

## Template context

Learn more about template context.

[Go this repo](https://github.com/Soopro/rafiki/)

https://github.com/Soopro/rafiki/blob/master/jinja2_template.md

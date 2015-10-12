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

First you have to enter the pyco folder obviously, then you can run pyco in multiple ways.

* `sh start.sh`: Run as backend. you will need `sh stop.sh` to stop it, or kill the system progress manually.

* `python pyco.py`: Run as develop.

## Usage

### Config

You can modify the `config.py` to change base settings.

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
  * `template`: given a default `template` alias base on `type` for content which don't have template attribute.
  * `marker`: parse content with short code marks.
  * `jinja_helper`: add multiple helpers and filters, learn more from the ***jinja2 template*** document of our system. Check [this repo](http://github.com/soopro/rafiki)

**Attation**: If you want build themes for our system, you should not change any thing about plugins, because our system might not support your modify.


### Content

Pyco is flat file CMS, there is no database. All content host as `.md` markdown file in `content` folder.

The type of contents is base on folder name. The files in the root of `content` folder is static page call 'page'. Add other content types just create a folder then put `.md` inside, the folder name will be `alias` of this content type.

There is global content data for whole site call **Site Meta**, to having this data, you have to put a `site.json` file in the root of `content` folder.


## Site.json

Global content data for whole site.

* `content_types`: **[ dict ]** content types is define by folder name, but those folder name is always a `alias`, given a Text title for content type here.

* `menus`: **[ dict ]** define multiple menus. Follow `menu` structure exactly.
  1. `< menu_alias >`: **[ list ]** a menu.
    * `alias`: **[ str ]** menu item alias
    * `title`: **[ str ]** menu item title
    * `link`: **[ str ]** menu link, system will generate `url` by `link`.
    * `meta`: **[ dict ]** menu item meta, put custom data in side as you wish.
    * `nodes`: **[ list ]** children menu items

* `meta`: Site meta
  * `alias`: **[ str ]** site alias. aka app alias
  * `title`: **[ str ]** site title. aka app title
  * `type`: **[ str ]** site type. aka app type
  * `logo`: **[dict]** media of logo
    * `src`: **[ str ]** media src.
    * `title`: **[ str ]** media title.
    * `link`: **[ str ]** media link if have one.
    * `target`: **[ str ]** target for media link. '\_blank' or something else.
    * `class`: **[ str ]** media class.

  * `author`: **[ str ]** author name.
  * `copyright`: **[ str ]** copyright.
  * `description`: **[ str ]** description text.
  * `license`: **[ str ]** license.
  * `locale`: **[ str ]** language locale.

  * `translates`: **[ dict ]** translates if you need.
    ```json
    {
       "zh_CN":{"name":"汉语","url":"http://....."},
       "en_US":{"name":"English","url":"http://....."}
    }
    ```

* `taxonomy`: **[ dict ]** All taxonomy host here. (also could be tax for short)
  * `< taxonomy_alias >`: Terms of this category, you only have to define
    1. `alias`: **[ str ]** term alias
    2. `title`: **[ str ]** term title
    3. `priority`: **[ int ]** term priority
    4. `taxonomy`: **[ str ]** alias of the taxonomy own this term
    5. `updated`: **[ int ]** updated timestamp. make a fake one if you want using pyco.
    6. `meta`: **[ dict ]** term data in meta.
    leave it empty if you don really need it.
      * `pic`: **[ str ]** pic for term display.
      * `parent`: **[ str ]** get parent terms alias.
      * ... *Custom fields*


***Example***
```json
{
  "content_types": {
    "post": "Posts",
    "page": "Pages"
  },
  "menus": {
    "primary": [
      {
        "alias": "home",
        "meta": {},
        "nodes": [],
        "title": "Home",
        "link": "/"
      },
      {
        "alias": "page",
        "meta": {},
        "nodes": [],
        "title": "Static Page",
        "link": "/page"
      }
    ]
  },
  "meta": {
    "alias":"pyco",
    "type":"ws",
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
  "taxonomy":{
    "category": {
      "title":"Category",
      "content_types": ["post"],
      "terms": [
        {"alias":"food","title":"Food","meta":{"pic":"","parent":""}, "priority": 0 },
        {"alias":"book","title":"Book","meta":{"pic":"","parent":""}, "priority": 0 }
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

<p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.</p>

```

## Template context

Learn more about template context. 

[Go this repo](https://github.com/Soopro/rafiki/)

https://github.com/Soopro/rafiki/blob/master/jinja2_template.md

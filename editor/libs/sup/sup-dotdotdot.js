/*
supDotdotdot

Author : Redy Ru
Email : redy.ru@gmail.com
License : 2014 MIT
Version 1.0.0

---- Usage ----
	suffix - a suffix end of the text. Cloud be html codes. default is '...';
	sticky - suffix is sticky with content or not. defalut is not. etc., 'consectetur adipiscing elit ...';

    On your html:
        <div sup-dotdotdot suffix='...'>
			<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.
			<p>laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
		</div>

*/

(function (angular) {
    'use strict';
    
    var supDotdotdot = angular.module('supDotdotdot',[]);

    supDotdotdot.directive('supDotdotdot', function () {
        return {
            scope: {
                suffix: '@',
                sticky: '@'
            },
            link: function (scope, element) {
                var suffix = scope.suffix,
                    sticky,
                    container = element[0],
                    lastchild,
                    innerElem,
                    t = 1,
                    temp, right,
                    overflow_elem, half_elem,within_limit,

                    overflow, addSuffix, locateOverflowElement, html_length, trim;

				if(!suffix){
					suffix='...';
				}
				
                overflow = function (html) {
                    var dif = html.scrollHeight - html.offsetHeight;
                    return   dif !== 0;
                };

                addSuffix = function () {
                    var p_suffix = suffix;
                    if (sticky) {
                        p_suffix = ' ' + suffix;
                    }
                    var container_backup = container.innerHTML;
                    temp = container.innerHTML.slice(0,
                            container.innerHTML.length - p_suffix.length);
                    container.innerHTML = temp + p_suffix;
                    var k = 1;
                    while (overflow(container)) {
                        container.innerHTML = container_backup;
                        temp = container.innerHTML.slice(0,
                                container.innerHTML.length - p_suffix.length - k);
                        k += 1;
                        container.innerHTML = temp + p_suffix;
                        console.log(container.innerHTML);
                        console.log('k ' + k);
                    }
                };

                locateOverflowElement= function (div) {
                    var elem = div;
                    innerElem = elem;
                    if (elem.children.length === 0) {
                        return elem;
                    }
                    while (elem.children.length !== 0) {
                        t += 1;
                        if (t > 100) {
                            return;
                        }
                        if (overflow(div)) {
                            lastchild = elem.childNodes[elem.childNodes.length - 1];
                            innerElem = elem;
                            lastchild.remove();
                            if (container.childNodes.length === 1) {
                                elem = container.childNodes[0];
                                if (!elem.children) {
                                    if (!overflow(div)) {
                                        elem = lastchild;
                                        innerElem.appendChild(lastchild);
                                        continue;
                                    }
                                    return lastchild;
                                }
                            }
                        } else {
                            elem = lastchild;
                            if (!elem.children) {
                                innerElem.appendChild(lastchild);
                                return elem;
                            }
                        }
                    }
                    innerElem.appendChild(lastchild);
                    lastchild = elem;
                    return lastchild;
                };

                html_length = function (html) {
                    return html.textContent.length;
                };

                half_elem = function (html) {
                    html.textContent = html.textContent.slice(0, html_length(html) / 2);
                };

                within_limit = function (new_elem, old_elem) {
                    var dif = new_elem.length - old_elem.length;
                    return dif < 1 && dif > -1;
                };

                trim = function (container, elem) {
                    right = elem.textContent.slice(html_length(elem) / 2, html_length(elem));
                    half_elem(elem);
                    while (overflow(container)) {
                        right = elem.textContent.slice(html_length(elem) / 2, html_length(elem));
                        half_elem(elem);
                        if (elem.textContent === '') {
                            elem.remove();
                            addSuffix();
                            return;
                        }
                        t += 1;
                        if (t > 100) {
                            return;
                        }
                    }
                    var left = elem.textContent;
                    var ori_left = left;
                    var old_html = left;
                    left = left + right.slice(0, right.length / 2);
                    var right_backup = right.slice(0, right.length / 2);
                    elem.textContent = left;
                    right = right.slice(right.length / 2, right.length);
                    t = 0;
                    while (overflow(container) || !within_limit(elem.textContent, old_html)) {
                        console.log('test : ' + t);
                        if (elem.textContent === '') {
                            elem.remove();
                            console.log('remove self');
                            return;
                        }
                        t += 1;
                        if (t > 100) {
                            return;
                        }
                        old_html = elem.textContent;
                        if (!overflow(container)) {
                            ori_left = left;
                            left = left + right.slice(0, right.length / 2);
                            right_backup = right.slice(0, right.length / 2);
                            elem.textContent = left;
                            right = right.slice(right.length / 2, right.length);
                        }
                        else {
                            left = ori_left + right_backup.slice(0, right_backup.length / 2);
                            right = right_backup.slice(right_backup.length / 2, right_backup.length);
                            right_backup = right_backup.slice(0, right_backup.length / 2);
                            elem.textContent = left;
                        }
                    }
                    if (elem.textContent === '') {
                        elem.remove();
                    }
                    addSuffix();
                };

                if (!element[0].hasAttribute('sticky')) {
                    sticky = false;
                }
                else {
                    sticky = scope.sticky !== 'false' || scope.sticky === undefined;
                }

                container.innerHTML = container.innerHTML.replace(/<!--[\s\S]*?-->/g, '');

                overflow_elem = locateOverflowElement(container);

                trim(container, overflow_elem);
            }
        };
    });
})(angular);
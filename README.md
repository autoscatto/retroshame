retroshame
==========

Unfortunate codebase for Retroshare


For now contains two painful bots, written only to test pyrs.
**I do not provide any guarantee on their effectiveness.**

  - chattino.py: join in all lobbies he sees, has a blacklist (which do not ever join), and a redlist in which he can not be killed. (with !kill in chan)
  - number5.py:  is a bot that interacts with the chan, launching specific methods for each match of the regular expression provided. (The name pays homage to the fabulous "SAINT Number 5" of [Short Circuit](http://www.imdb.com/title/tt0091949/) )

Use
-------- 

```sh

git clone https://github.com/drbob/pyrs.git
clone this repo
copy chosen bot to pyrs directory
create auth.txt with retroshare-nogui credential es:

    pwd yourpass
    port 7022
    user youruser
    host yourip

launch bot
profit

```




License
=========

```
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2013 Romain Lespinasse <romain.lespinasse@gmail.com>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
```

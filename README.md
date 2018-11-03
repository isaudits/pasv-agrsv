pasv-agrsv.py
===========

Passive recon / OSINT automation script:
- Runs passive recon tools specified in config file given a TLD
- Extracts email addresses, IP addresses, and DNS names from tool output using
regex
- Queries various OSINT sites specified in config file for TLD and saves result
to specified format (default pdf)
- Runs additional recon tools and website queries on IPs and DNS names found
from initial TLD analysis
- All identified domains, emails, ip addresses, dns names, and tool run history
/ output stored in sqlite database
- Aggressive mode can be enabled for running non-passive tests on discovered
hosts (e.g. screenshot and spider a website)

--------------------------------------------------------------------------------
## Notes
By default, the application runs in interactive mode allowing the user to select
a project name / output directory as well as add multiple TLDs for analysis
before executing scripted tasks. Optionally, a single domain can be specified
as a command line parameter to immediately create a new project and execute the
scripted tasks against that domain upon launch.

All scan parameters are pulled from config files so multiple configurations can
be developed and specified with the -c flag. An example config file
(default.example) is included and will be copied into the default path
(default.cfg) upon initial launch.

Please feel free to submit PR for bugfixes or additional tools/sites/regex for
default config file - any feedback, input, or improvement is greatly
appreciated!

Script tested on Kali Linux as well as OSX and should function on UNIX-based
systems with required dependencies.

--------------------------------------------------------------------------------
## Dependencies

### Python Module Dependencies:
- pyPdf (installed on Kali Linux by default)
- elixir `apt-get install python-elixir`

### Binary Dependencies:
- cutycapt (installed on Kali Linux by default)

### Dependencies in default tool config file:
- webshag (installed by default on Kali 1.x but not 2.x)
    `apt-get install webshag`

--------------------------------------------------------------------------------
## Todo
- Email domain filter currently only excludes emails not matching the active
domain during TLD phase
- HTML index page to summarize all output
- Scrape cutycapt output for targets & emails (convert to text first?)

--------------------------------------------------------------------------------

Copyright 2015

Matthew C. Jones, CPA, CISA, OSCP

IS Audits & Consulting, LLC - <http://www.isaudits.com/>

TJS Deemer Dana LLP - <http://www.tjsdd.com/>

Concept based upon functionality observed in the OSINT portion of the Kali
Discover script by leebaird: <https://github.com/leebaird/discover/>

--------------------------------------------------------------------------------

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
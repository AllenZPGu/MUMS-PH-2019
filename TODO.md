**TODO List**

List of tasks (so that we avoid overlap etc)

**Done**
- Changed puzzle access urls to /<act>/<scene>/ rather than /<title>/ (cosmetic change primarily)
- Changed access requirements
    - all except /puzzles
- Guards to check correct puzzle act + scene
- Create templates/PHapp/noGuesses.html

**In progress**
- Implemented metas
    - Mini-meta == scene 5
    - Meta 1 == act 7, scene 1
    - Meta 2 == act 7, scene 2
    - Colours script handles metas
- Idiomatic cleanup/streamlined database access

**Todo**
- Consolidate meta solve view with other puzzle solve view?
- Rework time calculations to use datetime.strptime
    - Not a priority
- Replace .format with f strings
- Add last_modified decorators to as many views as possible

- Rejig RELEASE_TIMES mechanism
    - Replace array with function; RELEASE_STAGE_FINAL global

- Resize cube

- Separate acts on /puzzles
- Check meta stats work correctly
    - Fix average solve time in /puzzlestats?
- Work out max capacity requirements and set up Heroku etc accordingly
- Fix last modified tag for cube data

- End of hunt
    - Solve page still accessible
    - etc....

- Policy question: on edit team members page, show whole form including currently added members?
- Unconvinced about 'AU' next to team name; could we replace this by an AUS flag emoji?
- Remove show/hide previous guesses?
    - (why not just show them...)
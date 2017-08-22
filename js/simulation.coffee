---
---

###
Build the individual simulation landing pages

Used by _include/simulation.html

Required variables:
  SIM_NAME: the directory name for the simulations from
    _data/simulations/SIM_NAME/meta.yaml
  DATA: the simulation data from the meta.yaml

Required tags:
  #summary
  #author
  #header
  #github_id
  #code
  #table
  #results_table
  #logo_image
  #youtube
  #images
###

{% include essential.coffee %}

select_tag = (tag) ->
  ### Select based on tag and bind the data

  Args:
    data: the data to add to the selection
    tag: the tag to select
  ###
  (x) -> d3.select(tag).selectAll().data(x).enter()


header = (sim_name) ->
  ### Add the header data

  Args:
    sim_name: the name of the simulation
  ###
  select_tag("#header")([sim_name])
    .append("a")
    .attr("href", (d) -> "{{ site.links.simmeta }}" + "/" + d + "/meta.yaml")
    .attr("target", "_blank")
    .text((d) -> d)


author = (data, sim_name) ->
  ### Add the author data

  Args:
    data: the simulation data
    sim_name: the name of the simulation
  ###
  select_tag("#author")([[data.metadata, sim_name]])
    .append("a")
    .attr("href", (d) -> "mailto:" + d[0].email + "?Subject=" + d[1])
    .attr("target", "_top")
    .text((d) -> d[0].author)


summary = (data) ->
  ### Add the summary data

  Args:
    data: the simulation data
  ###
  select_tag("#summary")([data.metadata.summary]).append("p").text((d) -> d)


github_icon = () ->
  ### Add the Github badge
  ###
  select_tag("#github_id")(['x'])
    .append("i")
    .attr("class", "material-icons prefix")
    .attr("style", "vertical-align: top; padding-left: 20px; padding-right: 3px")
    .append("img")
    .attr("style", "width: 22px; height: 22px; padding-bottom: 2px")
    .attr("src", "{{ site.baseurl }}" + "/images/github-black.svg")
    .attr("alt", "github")


github_id = (data) ->
  ### Add the Github user name

  Args:
    data: the simulation data
  ###
  select_tag("github_id")([data.metadata.github_id])
    .append("a")
    .attr("href", (d) -> "https://github.com/" + d)
    .attr("target", "_blank")
    .text((d) -> d)


github = (data) ->
  ### Add the Github badge and user name

  Args:
    data: the simualtion data
  ###
  if data.metadata.github_id isnt ""
    github_icon()
    github_id(data)


user_repo = (url) ->
  ### Construct the username/repo string from a Github URL

  Args:
    url: the Github URL

  Returns:
    the "user/repo" string
  ###
  /https:\/\/.*?\/(.*?)\/(.*?)\/.*/i
    .exec(url + "/a")[1..2]
    .join("/")


code = (data) ->
  ### Add the link to the code repository

  Args:
    data: the simulation data
  ###
  select_tag("#code")([data.metadata.implementation.repo.url])
    .append("a")
    .attr("href", (d) -> d)
    .attr("target", (d) -> "_blank")
    .text((d) -> user_repo(d))


benchmark = (data) ->
  ### Add the benchmark ID

  Args:
    data: the simulation data
  ###
  select_tag("#benchmark")([data.benchmark])
    .append("a")
    .attr("href", (d) -> "{{ site.baseurl }}" + "/benchmarks/benchmark" + d.id[0] + ".ipynb")
    .attr("target", "_blank")
    .text((d) -> d.id + "." + d.version)




to_date = (x) ->
  ### Change a time stamp into a date

  Args:
    x: timestamp with format "Tue Jan 31 21:01:55 EST 2017"

  Returns:
    date with format "Jan 31, 2017"
  ###
  format = (s) ->
    s[4..9] + ", " + s[11..14]
  format(new Date(Date.parse(x)).toString())



date = (data) ->
  ### Add the simulation date

  Args:
    data: the simulation date
  ###
  select_tag("#date")([data.metadata.timestamp])
    .append("span")
    .text((d) -> to_date(d))


get_software = (x) ->
  ### Get the software data that matches x

  Args:
    x: the name of the software to match

  Returns:
    the software data corresponding to x
  ###
  {{ site.data.codes | jsonify }}.filter((y) -> y.name.toLowerCase() is x)[0]


software = (data) ->
  ### Add the software name and link

  Args:
    data: the simulation date
  ###
  select_tag("#software")([data.metadata.software.name])
    .append("a")
    .attr("href", (d) -> get_software(d).home_page)
    .attr("target", "_blank")
    .text((d) -> d)


get_data = (data, name) ->
  ### Get the named data from the simulation data

  Args:
    data: the simulation data
    name: the name of the data

  Returns:
    the named data
  ###
  data.data.filter((x) -> x.name is name)[0]


memory_usage = (data) ->
  ### Get the memory usage for the simulation

  Args:
    data: the simulation data

  Returns:
    the memory usage string
  ###
  format = (x) ->
    x.value + " " + x.unit
  format(get_data(data, "memory_usage").values)


wall_time = (data) ->
  ### Get the simulation wall time

  Args:
    data: the simulation data

  Returns:
    the simulation wall time as a string
  ###
  get_data(data, "run_time").values[..].pop().wall_time + " s"


sim_time = (data) ->
  ### Get the simulation time

  Args:
    data: the simulation data

  Returns:
    the simulation time as a string
  ###
  get_data(data, "run_time").values[..].pop().sim_time + " s"


get_table_data = (data) ->
  ### The data for the results table

  Args:
    data: the simualation data

  Returns:
    data for the results table as a nested array
  ###
  return [
    ["Memory Usage", memory_usage(data)]
    ["Wall Time", wall_time(data)]
    ["Sim Time", sim_time(data)]
    ["Cores", "53"]
  ]


results_table = (data) ->
  ### Create the results table

  Args:
    data: the simulation data
  ###
  select_tag("#results_table")(get_table_data(data))
    .append("tr")
    .append("td")
    .text((d) -> d[0])
    .select(() -> this.parentNode)
    .append("td")
    .text((d) -> d[1])


add_card_image = (x) ->
  ### Add a card-image div

  Args:
    x: the current selection

  Returns:
    the div selection
  ###
  x.append("div")
    .attr("class", "card-image")
    .attr("style", "max-height: 70%")


add_card_image_ = (x) ->
  add_card_image(x)
    .append("img")
    .attr("class", "materialboxed responsive-img")


add_image = (x) ->
  ### Add a responsive image

  Args:
    x: the current selection

  Returns:
    the img selection
  ###
  add_card_image_(x).attr("src", (d) -> d.url)


add_youtube = (x) ->
  ### Add a youtube container

  Args:
    x: the current selection

  Returns:
    the iframe selection
  ###
  add_card_image(x)
    .append("div")
    .attr("class", "video-container")
    .append("iframe")
    .attr("frameborder", 0)
    .attr("allowfullscreen", '')
    .attr("src", (d) -> d.url)


add_description = (x) ->
  ### Add a card description

  Args:
    x: the current selection

  Returns:
    the p selection
  ###
  x.append("span")
    .attr("class", "card-content")
    .append("p")
    .text((d) -> d.description)


build_card = (addf) ->
  ### Make a card given a selection

  Args:
    addf: the content of the card

  Returns:
    a function for building a card
  ###
  sequence(
    (x) -> x.append("div").attr("class", "card small"),
    do_(addf),
    add_description
  )


card_bind = (type, tag, take_func=id) ->
  ### Bind data to a card selection

  Args:
    type: the type of the data either image or youtube
    tag: the tag element to append to
    take_: how much of the data to append

  Returns:
    a function to bind the data
  ###
  sequence(
    (x) -> x.data,
    filter((x) -> x.type is type),
    take_func,
    select_tag(tag),
  )


add_card = (addf, type, tag, with_div=id, take_func=take(1)) ->
  ### Constuct a data card

  Args:
    addf: the content of the card
    type: the type of the data either image or youtube
    tag: the tag element to append to
    with_div: function to add an extra div for columns
    take_func: data preprocessing function before bind

  Returns:
    a function to build the card
  ###
  sequence(
    card_bind(type, tag, take_func=take_func),
    with_div,
    build_card(addf)
  )


update_data = (x) ->
  ### Update chart data depending on name of the data

  Args:
    x: the data to update

  Returns:
    the updated data
  ###
  if x.data[0].name == "free_energy"
    x.axes[0].title = "Time"
    x.axes[1].title = "Free Energy"
    x.scales[0].type = "log"
    x.scales[1].type = "log"
  x.data[0].name = "the_data"
  delete x.data[0].type
  x


combine_data = curry(
  (chart_data, data) ->
    out = copy_(chart_data)
    out.data[0] = copy_(data)
    out
)


add_src = (x) ->
  ### Extract Vega chart as SVG url

  Args:
    x: the img selection to add the Vega src to
  ###
  new vega.View(vega.parse(x.datum()))
    .toImageURL("svg")
    .then((url) -> x.attr("src", url))


add_chart = (x) ->
  ### Build a div for a card with a Vega chart

  Args:
    x: the selection
  ###
  add_src(add_card_image_(x)
    .attr("style", "backgroud-color: white;"))


take_data = sequence(
  map(combine_data({{ site.data.charts.plot1d | jsonify }})),
  map(update_data)
)


add_card_col = (addf, type, take_func) ->
  ### Construct a data card in columns and rows for #images

  Args:
    addf: the content of the card
    type: the type of the data either image, line or youtube
    take_func: the data preprocessing function
  ###
  with_div = (x) -> x.append("div").attr("class", "col s4")
  add_card(addf, type, "#images", with_div=with_div, take_func=take_func)


build = (data, sim_name) ->
  ### Build the simulation landing page

  Args:
    data: the metadata for the simulation
    sim_name: the name of the simulation
  ###
  header(sim_name)
  author(data, sim_name)
  summary(data)
  github(data)
  code(data)
  benchmark(data)
  date(data)
  software(data)
  results_table(data)
  add_card(add_image, "image", "#logo_image")(data)
  add_card(add_youtube, "youtube", "#youtube")(data)
  add_card_col(add_image, "image", id)(data)
  add_card_col(add_chart, "line", take_data)(data)


build(DATA, SIM_NAME)

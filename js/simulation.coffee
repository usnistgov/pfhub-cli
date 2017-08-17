---
title: check
---

all_data = {{ site.data.simulations | jsonify }}
simmeta = "{{ site.links.simmeta }}"
baseurl = "{{ site.baseurl }}"
data_json = all_data[sim_name]['meta']
software = {{ site.data.codes | jsonify }}


get_selection = (data, tag) ->
  d3.select("#summary").selectAll().data([data]).enter()


summary = (data) ->
  selection = d3.select("#summary").selectAll().data([data]).enter()
  p = selection.append("p")
  p.text((d) -> d.metadata.summary)


author = (data) ->
  selection = d3.select("#author").selectAll().data([data]).enter()
  a = selection.append("a")
  a.attr("href", (d) -> "mailto:" + d.metadata.email + "?Subject=" + sim_name)
  a.attr("target", (d) -> "_top")
  a.text((d) -> d.metadata.author)


header = (data) ->
  selection = d3.select("#header").selectAll().data([data]).enter()
  a = selection.append("a")
  a.attr("href", (d) -> simmeta + "/" + sim_name + "/meta.yaml")
  a.attr("target", (d) -> "_blank")
  a.text((d) -> sim_name)


github_id = (data) ->
  selection = d3.select("#github_id").selectAll().data([data]).enter()
  i = selection.append("i")
  i.attr("class", (d) -> "material-icons prefix")
  i.attr("style", (d) -> "vertical-align: top; padding-left: 20px; padding-right: 3px")
  img = i.append("img")
  img.attr("style", (d) -> "width: 22px; height: 22px; padding-bottom: 2px")
  img.attr("src", (d) -> baseurl + "/images/github-black.svg")
  img.attr("alt", "github")
  a = selection.append("a")
  a.attr("href", (d) -> "https://github.com/" + d.metadata.github_id)
  a.attr("target", "_blank")
  a.text((d) -> d.metadata.github_id)


user_repo = (data) ->
  data_a = data + "/a"
  out = /https:\/\/.*?\/(.*?)\/(.*?)\/.*/i.exec data_a
  out[1] + "/" + out[2]


code = (data) ->
  selection = d3.select("#code").selectAll().data([data]).enter()
  a = selection.append("a")
  a.attr("href", (d) -> d.metadata.implementation.repo.url)
  a.attr("target", (d) -> "_blank")
  a.text((d) -> user_repo(d.metadata.implementation.repo.url))


get_software = (name) ->
  (s for s in software when s.name.toLowerCase() == name)[0]


table = (data) ->
  selection = d3.select("#table").selectAll().data([data]).enter()
  tr = selection.append("tr")

  td = tr.append("td")
  td.text("Benchmark")

  td = tr.append("td")
  a = td.append("a")
  a.attr("href", (d) -> baseurl + "/benchmarks/benchmark" + d.benchmark.id[0] + ".ipynb")
  a.attr("target", (d) -> "_blank")
  a.text((d) -> d.benchmark.id + "." + d.benchmark.version)

  tr = selection.append("tr")
  td = tr.append("td")
  td.text("Date")

  td = tr.append("td")

  make_date = (s) ->
    obj = new Date(Date.parse(s))
    s = obj.toString()
    return s.substring(4, 10) + ", " + s.substring(11, 15)

  td.text((d) -> make_date(d.metadata.timestamp))

  tr = selection.append("tr")
  td = tr.append("td")
  td.text("Code")
  td = tr.append("td")
  a = td.append("a")
  a.attr("href", (d) -> get_software(d.metadata.software.name).home_page)
  a.attr("target", (d) -> "_blank")
  a.text((d) -> d.metadata.software.name)


memory_usage = (data) ->
  v = (d for d in data.data when d.name == "memory_usage")[0]
  return v.values.value + " " + v.values.unit


wall_time = (data) ->
  v = (d for d in data.data when d.name == "run_time")[0]
  l = v.values.length
  return v.values[l - 1].wall_time + " s"


sim_time = (data) ->
  v = (d for d in data.data when d.name == "run_time")[0]
  l = v.values.length
  return v.values[l - 1].sim_time + " s"


results_table = (data) ->
  selection = d3.select("#results_table").selectAll().data([data]).enter()
  table_data = [
    ["Memory Usage", memory_usage(data)]
    ["Wall Time", wall_time(data)]
    ["Sim Time", sim_time(data)]
    ["Cores", "53"]
  ]
  for item in table_data
    tr = selection.append("tr")
    td = tr.append("td")
    td.text(item[0])
    td = tr.append("td")
    td.text(item[1])


get_images = (data) ->
   (d for d in data.data when (d.type == 'image'))


get_youtube = (data) ->
  (d for d in data.data when (d.type == "youtube"))[0]


logo_image = (data) ->
  images = [get_images(data)[0]]
  selection = d3.select("#logo_image").selectAll().data(images).enter()
  card_image(selection)


youtube = (data) ->
  selection = d3.select("#youtube").selectAll().data([data]).enter()
  div = selection.append("div")
  div.attr("class", "video-container")
  iframe = div.append("iframe")
  iframe.attr("frameborder", 0)
  iframe.attr("allowfullscreen")
  iframe.attr("src", (d) -> get_youtube(d).url)
  div = selection.append("div")
  div.attr("class", "flow-text")
  div.attr("style", "font-size: 16px")
  div.text((d) -> get_youtube(d).description)


card_image = (selection) ->
  div1 = selection.append("div")
  div1.attr("class", "card medium")
  div2 = div1.append("div")
  div2.attr("class", "card-image")
  img = div2.append("img")
  img.attr("class", "materialboxed responsive-img")
  img.attr("src", (d) -> d.url)
  div3 = div1.append("span")
  div3.attr("class", "card-content")
  p = div3.append("p")
  p.text((d) -> d.description)


card_images = (data) ->
  images = get_images(data)
  selection = d3.select("#images").selectAll().data(images).enter()
  div0 = selection.append("div")
  div0.attr("class", "col s6")
  card_image(div0)


header(data_json)
summary(data_json)
author(data_json)
if data_json.metadata.github_id != ""
  github_id(data_json)
code(data_json)
table(data_json)
results_table(data_json)
logo_image(data_json)
youtube(data_json)
card_images(data_json)


add_chart = (chart_json) ->
  selection = d3.select("#images").selectAll().data([chart_json]).enter()

  div = selection.append("div")
  div.attr("class", "col s6")

  div1 = div.append("div")
  div1.attr("class", "card medium")

  div2 = div1.append("div")
  div2.attr("class", "card-image")

  img = div2.append("img")
  img.attr("class", "materialboxed responsive-img")
  img.attr("id", "chart")

  div3 = div1.append("span")
  div3.attr("class", "card-content")

  p = div3.append("p")
  p.text((d) -> "My Graph")

  view = new vega.View(vega.parse(chart_json))
    .initialize("#chart")
    .renderer('svg')
    .hover()
    .run()

chart_json = {{ site.data.charts | jsonify }}['1a1_free_energy']
add_chart(chart_json)

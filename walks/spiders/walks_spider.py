import scrapy
import json

class WalkSpider(scrapy.Spider):
	name = 'walks'

	start_urls = ['https://www.aussiebushwalking.com/world']

	def parse(self, response):
		# Follow links to walks
		for href in response.css('.walkBox h4 a::attr(href)'):
			yield response.follow(href, self.parse_walk)

		# Follow link to next page
		# for href in response.css('.pagination .next  a::attr(href)'):
		# yield response.follow(href, self.parse)

	def parse_walk(self, response):
			
		def extract_with_css(query):
			return response.css(query).extract_first().strip()
		
		def extract_stat_with_xpath(arrayIndex):
			selector = '//div[@class="homeLists"]/div/div[@class="stat"][%s]/span/text()' % arrayIndex
			return response.xpath(selector).extract()

		def duration_in_min(arrayIndex):
			data = extract_stat_with_xpath(arrayIndex)
			
			try:
				time =  float(data[0])
			except ValueError:
				time = json.dumps(None)
			
			try:
				unit = data[1]
			except IndexError:
				unit = None
	
			if unit == 'days':
				return time*24*60
			elif unit  == 'hrs' or unit == 'hr':
				return time*60
			elif unit  == 'mins':
				return time
			else:
				return time

		yield {
			'name': extract_with_css('div.intro h2::text'),
			'url': response.url,
			'state': response.url.split('/')[3],
			'location': extract_with_css('div.intro a::text'),
			'distance': response.xpath('//div[@class="homeLists"]/div/div[@class="stat"][2]/span/text()').extract(),
			'duration': duration_in_min(3),
			'difficulty': extract_with_css('.stat div::text'),
			'features': response.css('.tagViewer .tagViewLabel::text').extract(),
			'description': extract_with_css('.midBar p::text'),
		}

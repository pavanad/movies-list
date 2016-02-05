#!usr/bin/python
# -*- coding: utf-8 -*-

"""
Movies List - Web Scraping 

this is a tool for data collection in movies download sites.

@author: pavan <adilson.pavan@gmail.com>
"""


import sys
import requests


def get_href(line, index):
	start = line.find('href="', index) + 6
	end = line.find('"', start)
	return line[start:end]


def get_total_pages(line, index):
	link = get_href(line, index)
	return int(link.split('/')[-1])


class YesFilmes:

	url = ''
	total_pages = 0
	movies_list = []

	def __init__(self):
		self.url = 'http://yesfilmes.org/'
		self.total_pages = 0


	def get_content_page(self, response, first_page=False):

		content = response.content.split('\n')

		title = []
		quality = []
		audio = []
		video = []
		for line in content:
			if first_page:
				last = line.find('class="last"')
				if last != -1:
					self.total_pages = get_total_pages(line, last)

			# get post title
			post = line.find('rel="bookmark"')
			if post != -1:
				end = line.find('</a>', post + 15)
				title.append(line[post + 15:end])
						

			# get quality
			q = line.find('Qualidade:')
			if q != -1:
				quality.append(line.strip('<br />'))

			# get audio quality
			audio_quality = line.find('Qualidade de Áudio:')
			if audio_quality != -1:
				end = line.find('<br />', audio_quality + 20)
				audio.append(int(line[audio_quality + 20:end].strip(' ')))

			# get video quality
			video_quality = line.find('Qualidade de Vídeo:')
			if video_quality != -1:
				end = line.find('</p>', video_quality + 20)
				video.append(int(line[video_quality + 20:end].strip(' ')))

		for (t,q,a,v) in zip(title, quality, audio, video):
			self.movies_list.append({
				'title': t, 
				'quality': q, 
				'audio': a,
				'video': v
			})


	def parse(self):

		pages = 10
		response = requests.get(self.url)
		
		if response.status_code == 200:
			
			print '\nMovies list: starting search movies...'
			self.get_content_page(response, True)

			for i in range(pages+1)[2:]:
				response = requests.get(self.url + '/page/' + str(i))
				self.get_content_page(response)

			for item in self.movies_list:
				print '\nTitle: ' + item['title']
				print item['quality']
				print 'Audio: ' + str(item['audio'])
				print 'Video: ' + str(item['video'])

			print '\ntotal pages: %d \n' % self.total_pages

		else:
			print 'Movies list: could not open url (status code: %s)' % str(response.status_code)
			exit()


if __name__ == '__main__':
	#for arg in sys.argv[1:]:
	#	print arg

	yesfilmes = YesFilmes()
	yesfilmes.parse()


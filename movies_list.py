#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Movies List - Web Scraping 

this is a tool for data collection in movies download sites.

@author: pavan <adilson.pavan@gmail.com>
"""


import sys
import getopt
import requests


def get_href(line, index=0):	
	start = line.find('href="',index) + 6
	end = line.find('"', start)
	return line[start:end]


def get_total_pages(line, index):
	link = get_href(line, index)
	return int(link.split('/')[-1])


def is_digit(arg):
	if arg.isdigit():
		return int(arg)
	else:
		print 'Movies list: arg must be a number'
		exit()


def usage():
	print '\nUsage:'
	print '\n    python movies_list.py [<options>]'
	print '\nOptions:'
	print '\n-p, --pages \t Set number of pages (default=1)'
	print '-a, --audio \t Set audio quality [0-10] (default=10)'
	print '-v, --video \t Set video quality [0-10] (default=10)'
	print '-t, --torrent \t Search movies for download torrent (default=False)\n'


class YesFilmes:

	url = ''
	total_pages = 0
	movies_list = []
	pages = 1
	audio = 10
	video = 10
	torrent = False


	def __init__(self):
		self.url = 'http://yesfilmes.org/'
		self.total_pages = 0


	def set_pages(self, pages):
		self.pages = pages


	def set_audio(self, audio):
		self.audio = audio


	def set_video(self, video):
		self.video = video


	def set_torrent(self, torrent):
		self.torrent = torrent


	def get_link_torrent(self, link):

		response = requests.get(link)		
		if response.status_code == 200:
		
			content = response.content.split('\n')
			for line in content:
				torrent = line.find('title="Torrent"')
				if torrent != -1:
					return get_href(line)
		return None


	def get_content_page(self, response, first_page=False):

		content = response.content.split('\n')

		title = []
		quality = []
		audio = []
		video = []
		more = []
		torrent = []
		for line in content:
			if first_page:
				last = line.find('class="last"')
				if last != -1:
					self.total_pages = get_total_pages(line, last)

			# get link download
			more_link = line.find('class="more-link"')
			if more_link != -1:	
				link = get_href(line)			
				more.append(link)

				if self.torrent:
					link_torrent = self.get_link_torrent(link)
					torrent.append(link_torrent)
				else:
					torrent.append('')		

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


		for (t,q,a,v,m,tt) in zip(title, quality, audio, video, more, torrent):
			if a == self.audio and v == self.video:
				self.movies_list.append({
					'title': t, 
					'quality': q, 
					'audio': a,
					'video': v,
					'more': m,
					'torrent': tt
				})


	def parse(self):

		response = requests.get(self.url)
		
		if response.status_code == 200:
			
			print '\nMovies list: starting search movies...'
			self.get_content_page(response, True)

			for i in range(self.pages+1)[2:]:
				response = requests.get(self.url + '/page/' + str(i))
				self.get_content_page(response)

			for item in self.movies_list:
				print '\nTitle: ' + item['title']
				print item['quality']
				print 'Audio: ' + str(item['audio'])
				print 'Video: ' + str(item['video'])
				print 'More: ' + str(item['more'])

				if self.torrent: 
					print 'Torrent: ' + str(item['torrent'])

			print '\nSearch for %d of %d pages \n' % (self.pages, self.total_pages)

		else:
			print 'Movies list: could not open url (status code: %s)' % str(response.status_code)
			exit()


def main(argv):
	
	try:
		opts, args  = getopt.getopt(argv,'p:a:v:th', ['pages=', 'audio=', 'video=', 'torrent', 'help'])
	except getopt.GetoptError:
		usage()
		exit()

	yesfilmes = YesFilmes()

	for opt, arg in opts:
		if opt in ('-p', '--pages'):
			pages = is_digit(arg)	
			yesfilmes.set_pages(pages)		
		elif opt in ('-a', '--audio'):
			audio = is_digit(arg)
			yesfilmes.set_audio(audio)
		elif opt in ('-v', '--video'):
			video = is_digit(arg)
			yesfilmes.set_video(video)
		elif opt in ('-t', '--torrent'):
			yesfilmes.set_torrent(True)
		elif opt in ('-h', '--help'):
			usage()
			exit()

	yesfilmes.parse()


if __name__ == '__main__':
	main(sys.argv[1:])

	


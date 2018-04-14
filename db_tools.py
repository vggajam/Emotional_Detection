file_name = './template_features.csv'
place = 'template'
new_file_name = './tmp.csv'
import csv
import datetime as dt

TF = "%a %b %d %H:%M:%S %z %Y"
def prop_format(file_name,place,new_file_name):
    reader = csv.reader(open(file_name))
    _ = next(reader)
    # print(header)
    new_header = ['id_str','user_id','place','tdate','ttime','containsText','deg_adv', 'adv_cnt', 'containsImage', 'fct1', 'fct2', 'fct3', 'fct4', 'fct5', 'fct6', 'fct7', 'fct8', 'fct9', 'fct10', 'fct11', 'fct12', 'fct13', 'fct14', 'fct15', 'sat_mean', 'sat_cntrst', 'brit_mean',
    'brit_cntrst', 'warm/cool', 'clear/dull', 'containsSocial', 'reply_cnt', 'retweet_cnt', 'likes', 'mentions', 'retweet?', 'reply?', 'hour0', 'hour1', 'hour2', 'hour3', 'hour4', 'hour5', 'hour6', 'hour7', 'hour8', 'hour9', 'hour10', 'hour11', 'hour12', 'hour13', 'hour14', 'hour15', 'hour16', 'hour17', 'hour18', 'hour19', 'hour20', 'hour21', 'hour22', 'hour23', 'imagetweet?', 'originalTweet?', 'query?', 'sharingtweet?', 'function', 'pronoun', 'ppron ', 'i', 'we ', 'you', 'shehe', 'they', 'ipron', 'article', 'prep', 'auxverb', 'adverb', 'conj', 'negate', 'verb', 'adj', 'compare', 'interrog', 'number', 'quant', 'affect', 'posemo', 'negemo', 'anx', 'anger', 'sad', 'social', 'family', 'friend', 'female', 'male', 'cogproc', 'insight', 'cause', 'discrep', 'tentat', 'certain', 'differ', 'percept', 'see', 'hear', 'feel', 'bio', 'body', 'health', 'sexual', 'ingest', 'drives', 'affiliation', 'achieve', 'power', 'reward', 'risk', 'focuspast', 'focuspresent', 'focusfuture', 'relativ', 'motion', 'space', 'time', 'work', 'leisure', 'home', 'money', 'relig', 'death', 'informal', 'swear', 'netspeak', 'assent', 'nonflu', 'filler', 'period', 'comma', 'colon', 'semic', 'qmark', 'exclaim', 'dash', 'quote', 'apostro', '3dots', 'parenth', 'posemoji', 'negemoji', 'neuemoji']
    final_table = list()
    for row in reader:
        new_row = list()
        new_row+= row[0:2]
        if not str(new_row[0]).startswith('ID'):
            new_row[0]='ID'+new_row[0]
        new_row+= [place]
        new_row += [str(dt.datetime.strptime(row[2], TF).date().strftime(r"%Y-%m-%d"))]
        new_row +=[str(dt.datetime.strptime(row[2], TF).time())]
        new_row +=[row[3]]
        new_row +=row[12:14]
        new_row +=row[14:]
        final_table.append(new_row)
    csv.writer(open(new_file_name,'w',newline='')).writerows([new_header]+final_table)
# prop_format('./csv_files/banglore_features.csv','mumbai','./new_banglore_features.csv')
def prop_format_2(csv_file, new_csv_file):
    pen = csv.reader(open(csv_file))
    data_table = list()
    for row in pen:
        row.insert(2,'selected')
        data_table.append(row)
    csv.writer(open(new_csv_file,'w',newline='')).writerows(data_table)

prop_format_2('./selected_features.csv','./new_selected.csv')
"""
CREATE TABLE `tweets` (
  `id_str` varchar(21) NOT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `place` varchar(10) DEFAULT NULL,
  `tdate` date DEFAULT NULL,
  `ttime` time DEFAULT NULL,
  `containsText` tinyint(4) DEFAULT NULL,
  `deg_adv` double DEFAULT NULL,
  `adv_cnt` double DEFAULT NULL,
  `containsImage` tinyint(4) DEFAULT NULL,
  `fct1` double DEFAULT NULL,
  `fct2` double DEFAULT NULL,
  `fct3` double DEFAULT NULL,
  `fct4` double DEFAULT NULL,
  `fct5` double DEFAULT NULL,
  `fct6` double DEFAULT NULL,
  `fct7` double DEFAULT NULL,
  `fct8` double DEFAULT NULL,
  `fct9` double DEFAULT NULL,
  `fct10` double DEFAULT NULL,
  `fct11` double DEFAULT NULL,
  `fct12` double DEFAULT NULL,
  `fct13` double DEFAULT NULL,
  `fct14` double DEFAULT NULL,
  `fct15` double DEFAULT NULL,
  `sat_mean` double DEFAULT NULL,
  `sat_contrast` double DEFAULT NULL,
  `brit_mean` double DEFAULT NULL,
  `brit_contrast` double DEFAULT NULL,
  `warm/cool` double DEFAULT NULL,
  `clear/dull` double DEFAULT NULL,
  `containsSocial` tinyint(4) DEFAULT NULL,
  `replies_cnt` double DEFAULT NULL,
  `retweets_cnt` double DEFAULT NULL,
  `likes_cnt` double DEFAULT NULL,
  `mentions_cnt` double DEFAULT NULL,
  `retweet?` double DEFAULT NULL,
  `reply?` double DEFAULT NULL,
  `hour0` double DEFAULT NULL,
  `hour1` double DEFAULT NULL,
  `hour2` double DEFAULT NULL,
  `hour3` double DEFAULT NULL,
  `hour4` double DEFAULT NULL,
  `hour5` double DEFAULT NULL,
  `hour6` double DEFAULT NULL,
  `hour7` double DEFAULT NULL,
  `hour8` double DEFAULT NULL,
  `hour9` double DEFAULT NULL,
  `hour10` double DEFAULT NULL,
  `hour11` double DEFAULT NULL,
  `hour12` double DEFAULT NULL,
  `hour13` double DEFAULT NULL,
  `hour14` double DEFAULT NULL,
  `hour15` double DEFAULT NULL,
  `hour16` double DEFAULT NULL,
  `hour17` double DEFAULT NULL,
  `hour18` double DEFAULT NULL,
  `hour19` double DEFAULT NULL,
  `hour20` double DEFAULT NULL,
  `hour21` double DEFAULT NULL,
  `hour22` double DEFAULT NULL,
  `hour23` double DEFAULT NULL,
  `imagetweet?` double DEFAULT NULL,
  `originalTweet?` double DEFAULT NULL,
  `query?` double DEFAULT NULL,
  `sharingtweet?` double DEFAULT NULL,
  `function` double DEFAULT NULL,
  `pronoun` double DEFAULT NULL,
  `ppron` double DEFAULT NULL,
  `i` double DEFAULT NULL,
  `we` double DEFAULT NULL,
  `you` double DEFAULT NULL,
  `shehe` double DEFAULT NULL,
  `they` double DEFAULT NULL,
  `ipron` double DEFAULT NULL,
  `article` double DEFAULT NULL,
  `prep` double DEFAULT NULL,
  `auxverb` double DEFAULT NULL,
  `adverb` double DEFAULT NULL,
  `conj` double DEFAULT NULL,
  `negate` double DEFAULT NULL,
  `verb` double DEFAULT NULL,
  `adj` double DEFAULT NULL,
  `compare` double DEFAULT NULL,
  `interrog` double DEFAULT NULL,
  `number` double DEFAULT NULL,
  `quant` double DEFAULT NULL,
  `affect` double DEFAULT NULL,
  `posemo` double DEFAULT NULL,
  `negemo` double DEFAULT NULL,
  `anx` double DEFAULT NULL,
  `anger` double DEFAULT NULL,
  `sad` double DEFAULT NULL,
  `social` double DEFAULT NULL,
  `family` double DEFAULT NULL,
  `friend` double DEFAULT NULL,
  `female` double DEFAULT NULL,
  `male` double DEFAULT NULL,
  `cogproc` double DEFAULT NULL,
  `insight` double DEFAULT NULL,
  `cause` double DEFAULT NULL,
  `discrep` double DEFAULT NULL,
  `tentat` double DEFAULT NULL,
  `certain` double DEFAULT NULL,
  `differ` double DEFAULT NULL,
  `percept` double DEFAULT NULL,
  `see` double DEFAULT NULL,
  `hear` double DEFAULT NULL,
  `feel` double DEFAULT NULL,
  `bio` double DEFAULT NULL,
  `body` double DEFAULT NULL,
  `health` double DEFAULT NULL,
  `sexual` double DEFAULT NULL,
  `ingest` double DEFAULT NULL,
  `drives` double DEFAULT NULL,
  `affiliation` double DEFAULT NULL,
  `achieve` double DEFAULT NULL,
  `power` double DEFAULT NULL,
  `reward` double DEFAULT NULL,
  `risk` double DEFAULT NULL,
  `focuspast` double DEFAULT NULL,
  `focuspresent` double DEFAULT NULL,
  `focusfuture` double DEFAULT NULL,
  `relativ` double DEFAULT NULL,
  `motion` double DEFAULT NULL,
  `space` double DEFAULT NULL,
  `time` double DEFAULT NULL,
  `work` double DEFAULT NULL,
  `leisure` double DEFAULT NULL,
  `home` double DEFAULT NULL,
  `money` double DEFAULT NULL,
  `relig` double DEFAULT NULL,
  `death` double DEFAULT NULL,
  `informal` double DEFAULT NULL,
  `swear` double DEFAULT NULL,
  `netspeak` double DEFAULT NULL,
  `assent` double DEFAULT NULL,
  `nonflu` double DEFAULT NULL,
  `filler` double DEFAULT NULL,
  `period` double DEFAULT NULL,
  `comma` double DEFAULT NULL,
  `colon` double DEFAULT NULL,
  `semic` double DEFAULT NULL,
  `qmark` double DEFAULT NULL,
  `exclaim` double DEFAULT NULL,
  `dash` double DEFAULT NULL,
  `quote` double DEFAULT NULL,
  `apostro` double DEFAULT NULL,
  `3dots` double DEFAULT NULL,
  `parenth` double DEFAULT NULL,
  `posemoji` double DEFAULT NULL,
  `negemoji` double DEFAULT NULL,
  `neuemoji` double DEFAULT NULL,
  PRIMARY KEY (`id_str`),
  UNIQUE KEY `id_str_UNIQUE` (`id_str`),
  KEY `place` (`place`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
"""
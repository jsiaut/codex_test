from authored_helpers import save,authored_anonymous_related_table
h='| | (In millions) | | | | | | | | | | | | | |'
r='Total net revenue | | $ | 200 | | | $ | 71 | | | $ | 382 | | | $ | 148 |'
e='Total costs and expenses, including inventory purchases | | $ | 31 | | | $ | 46 | | | $ | 67 | | | $ | 65 |'
s='| | (In millions) | | | | | |\nTotal receivables | | $ | 76 | | | $ | 31 |\nTotal payables | | $ | 8 | | | $ | 12 |'
rows=authored_anonymous_related_table('Broadcom',[
 ('2018-02-05','2018-05-06'),('2017-01-30','2017-04-30'),
 ('2017-10-30','2018-05-06'),('2016-10-31','2017-04-30')],
 h+'\n'+r,['200','71','382','148'],h+'\n'+r+'\n'+e,['31','46','67','65'],
 s,['2018-05-06','2017-10-29'],['76','31'],['8','12'])
save('04c04d0c2e5ff7103f26aa9c19621b1557bba53c02af97ad594412dfe0ef9643',rows)

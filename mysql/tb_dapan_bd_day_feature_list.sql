DROP TABLE IF EXISTS `tb_dapan_bd_day_feature_list`;
CREATE TABLE `tb_dapan_bd_day_feature_list` (  
    `id` int(11) NOT NULL AUTO_INCREMENT,  
    `day`  int(11) NOT NULL DEFAULT 0,
    `fid`  varchar(24) NOT NULL DEFAULT '',  
    `fname`  text NOT NULL DEFAULT '',  
    `val` float(11) NOT NULL DEFAULT 0,  
    `status` int(11) NOT NULL DEFAULT 0,  
    `uptime` int(11) NOT NULL DEFAULT 0,  
    INDEX(`day`),
    PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;

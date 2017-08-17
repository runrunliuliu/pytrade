DROP TABLE IF EXISTS `tb_dapan_bd_day_list`;
CREATE TABLE `tb_dapan_bd_day_list` (  
    `id` int(11) NOT NULL AUTO_INCREMENT,  
    `day`  int(11) NOT NULL DEFAULT 0,  
    `status` int(11) DEFAULT 0,  
    `predict` int(11) NOT NULL DEFAULT 0,  
    `prob` float(11) NOT NULL DEFAULT 0,  
    `pday` varchar(20) NOT NULL DEFAULT '',  
    `uptime` int(11) NOT NULL DEFAULT 0,  
    INDEX(`day`),
    PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;

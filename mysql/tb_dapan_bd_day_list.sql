DROP TABLE IF EXISTS `tb_dapan_bd_day_list`;
CREATE TABLE `tb_dapan_bd_day_list` (  
    `id` int(11) NOT NULL AUTO_INCREMENT,  
    `day`  varchar(12),  
    `status` int(11) DEFAULT '0',  
    `predict` int(11) NOT NULL,  
    `prob` float(11) NOT NULL,  
    `pday` varchar(20) NOT NULL,  
    INDEX(`day`),
    PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;

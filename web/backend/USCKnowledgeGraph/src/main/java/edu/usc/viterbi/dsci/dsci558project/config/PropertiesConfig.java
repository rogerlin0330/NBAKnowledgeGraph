package edu.usc.viterbi.dsci.dsci558project.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Properties;

@Configuration
public class PropertiesConfig {

    @Bean("druidPoolProps")
    @ConfigurationProperties(prefix = "spring.datasource.druid")
    public Properties druidPoolProps() {
        return new Properties();
    }

    @Bean("mysqlConnProps")
    @ConfigurationProperties(prefix = "spring.datasource.mysql")
    public Properties mysqlConnProps() {
        return new Properties();
    }

    @Bean("mysqlPageInterceptorProps")
    @ConfigurationProperties(prefix = "mybatis.pageinterceptor.mysql")
    public Properties mysqlPageInterceptorProps() {
        return new Properties();
    }

}

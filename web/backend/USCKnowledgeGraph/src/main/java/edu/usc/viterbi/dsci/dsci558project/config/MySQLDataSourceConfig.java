package edu.usc.viterbi.dsci.dsci558project.config;

import com.alibaba.druid.pool.DruidDataSource;
import com.github.pagehelper.PageInterceptor;
import org.apache.ibatis.plugin.Interceptor;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;

import javax.sql.DataSource;
import java.sql.SQLException;
import java.util.Properties;

@Configuration
@MapperScan(basePackages = "edu.usc.viterbi.dsci.dsci558project.dao",
        sqlSessionFactoryRef = "mysqlSqlSessionFactory")
public class MySQLDataSourceConfig {

    @Autowired
    @Qualifier("druidPoolProps")
    private Properties druidPoolProps;
    @Autowired
    @Qualifier("mysqlConnProps")
    private Properties mysqlConnProps;
    @Autowired
    @Qualifier("mysqlPageInterceptorProps")
    private Properties mysqlPageInterceptorProps;

    @Bean("mysqlDataSource")
    @DependsOn({"mysqlConnProps", "druidPoolProps"})
    public DataSource mysqlDataSource() throws SQLException {
        DruidDataSource mysqlDataSource = new DruidDataSource();

        mysqlDataSource.setDriverClassName(mysqlConnProps.getProperty("driver-class-name"));
        mysqlDataSource.setUrl(mysqlConnProps.getProperty("url"));
        mysqlDataSource.setUsername(mysqlConnProps.getProperty("username"));
        mysqlDataSource.setPassword(mysqlConnProps.getProperty("password"));

        mysqlDataSource.setInitialSize(Integer.parseInt(druidPoolProps.getProperty("initial-size")));
        mysqlDataSource.setMaxActive(Integer.parseInt(druidPoolProps.getProperty("max-active")));
        mysqlDataSource.setMinIdle(Integer.parseInt(druidPoolProps.getProperty("min-idle")));
        mysqlDataSource.setMaxWait(Long.parseLong(druidPoolProps.getProperty("max-wait")));
        mysqlDataSource.setPoolPreparedStatements(
                Boolean.parseBoolean(druidPoolProps.getProperty("pool-prepared-statements"))
        );
        mysqlDataSource.setValidationQuery(druidPoolProps.getProperty("validation-query"));
        mysqlDataSource.setValidationQueryTimeout(
                Integer.parseInt(druidPoolProps.getProperty("validation-query-timeout"))
        );
        mysqlDataSource.setTestOnBorrow(Boolean.parseBoolean(druidPoolProps.getProperty("test-on-borrow")));
        mysqlDataSource.setTestOnReturn(Boolean.parseBoolean(druidPoolProps.getProperty("test-on-return")));
        mysqlDataSource.setTestWhileIdle(Boolean.parseBoolean(druidPoolProps.getProperty("test-while-idle")));
        mysqlDataSource.setTimeBetweenEvictionRunsMillis(
                Long.parseLong(druidPoolProps.getProperty("time-between-eviction-runs-millis"))
        );
        mysqlDataSource.setMinEvictableIdleTimeMillis(
                Long.parseLong(druidPoolProps.getProperty("min-evictable-idle-time-millis"))
        );
        mysqlDataSource.setMaxEvictableIdleTimeMillis(
                Long.parseLong(druidPoolProps.getProperty("max-evictable-idle-time-millis"))
        );
        mysqlDataSource.setFilters(druidPoolProps.getProperty("filters"));

        return mysqlDataSource;
    }

    @Bean("mysqlPageInterceptor")
    @DependsOn("mysqlPageInterceptorProps")
    public PageInterceptor mysqlPagePageInterceptor() {
        PageInterceptor mysqlPageInterceptor = new PageInterceptor();
        mysqlPageInterceptor.setProperties(mysqlPageInterceptorProps);
        return mysqlPageInterceptor;
    }

    @Bean("mysqlSqlSessionFactory")
    @DependsOn({"mysqlDataSource", "mysqlPageInterceptor"})
    public SqlSessionFactory mysqlSqlSessiongFactory() throws Exception {
        SqlSessionFactoryBean sqlSessionFactory = new SqlSessionFactoryBean();
        sqlSessionFactory.setDataSource(mysqlDataSource());

        Resource mybatisConfig = new ClassPathResource("mybatis-config.xml");
        sqlSessionFactory.setConfigLocation(mybatisConfig);

        Interceptor[] interceptors = new Interceptor[]{mysqlPagePageInterceptor()};
        sqlSessionFactory.setPlugins(interceptors);

        return sqlSessionFactory.getObject();
    }

}

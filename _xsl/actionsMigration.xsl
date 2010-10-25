<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                version="1.0">
 
  <xsl:output method="xml" indent="yes" />

  <xsl:template match="/">
    <object name="portal_actions"
	    meta_type="CMF Actions Tool"
	    xmlns:i18n="http://xml.zope.org/namespaces/i18n">
      
      <xsl:for-each select="/actions-tool/action-provider/action">
	<xsl:variable name="category" select="@category"/>
	<xsl:if test="count((preceding-sibling::action|../preceding-sibling::action-provider/action)[@category=$category])=0">
	  
	  <xsl:call-template name="action_category">
	    <xsl:with-param name="category" select="$category"/>
	  </xsl:call-template>
	  
	</xsl:if>
      </xsl:for-each>
    </object>
  </xsl:template>
  
  <xsl:template name="action_category">
    <xsl:param name="category"/>

    <object meta_type="CMF Action Category">
      <xsl:attribute name="name">
	<xsl:value-of select="$category"/>
      </xsl:attribute>
      
      <property name="title"></property>

      <xsl:for-each select="//action[@category=$category]">
	
	<object meta_type="CMF Action" i18n:domain="plinn">
	  <xsl:attribute name="name">
	    <xsl:value-of select="@action_id"/>
	  </xsl:attribute>
	  
	  <property name="title" i18n:translate="">
	    <xsl:value-of select="@title"/>
	  </property>
	  
	  <property name="description"></property>

	  <property name="url_expr">
	    <xsl:value-of select="@url_expr"/>
	  </property>

	  <property name="icon_expr"></property>

	  <property name="available_expr">
	    <xsl:value-of select="@condition_expr"/>
	  </property>

	  <property name="permissions">
	    <xsl:for-each select="permission">
	      <element>
		<xsl:attribute name="value">
		  <xsl:value-of select="."/>
		</xsl:attribute>
	      </element>
	    </xsl:for-each>
	  </property>

	  <property name="visible">
	    <xsl:value-of select="@visible"/>
	  </property>

	</object>

      </xsl:for-each>

    </object>

  </xsl:template>

</xsl:stylesheet>
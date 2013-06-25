<script type="text/javascript" src="${src}"></script>
<script type="text/javascript">
  //<![CDATA[
  Raven.config('${dsn}', {
      'whitelistUrls': [
        % for item in hosts:
          /${item}/${not loop.last and ',' or ''}
        % endfor
      ],
      'includePaths': [
        % for item in hosts:
          /\/\/${item}/${not loop.last and ',' or ''}
        % endfor
      ]
  }).install();
  //]]>
</script>

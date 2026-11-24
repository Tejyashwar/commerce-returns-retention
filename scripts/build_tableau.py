"""Author fresh Tableau worksheets and dashboards from SQL-generated CSVs."""
import csv
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET


def el(parent, tag, text=None, **attrs):
    node = ET.SubElement(parent, tag, {k.replace('_', '-'): str(v) for k,v in attrs.items()})
    if text is not None:
        node.text = str(text)
    return node


def build_tableau(root):
    folder = root / 'tableau'
    (folder / 'Data').mkdir(exist_ok=True)
    files = ['overview', 'monthly', 'category', 'region', 'segments', 'repeat_90d', 'retention_summary']
    workbook = ET.Element('workbook', {'original-version':'18.1', 'source-build':'2026.3.0', 'source-platform':'mac', 'version':'18.1'})
    prefs = el(workbook, 'preferences')
    el(prefs, 'preference', name='ui.encoding.shelf.height', value='24')
    sources = el(workbook, 'datasources')
    definitions = {}
    for name in files:
        shutil.copyfile(root/'data/exports'/f'{name}.csv', folder/'Data'/f'{name}.csv')
        rows = list(csv.DictReader((folder/'Data'/f'{name}.csv').open()))
        fields = {}
        ds = el(sources, 'datasource', caption=name.replace('_',' ').title(), inline='true', name=f'textscan.{name}', version='18.1')
        cn = el(ds, 'connection', **{'class':'textscan', 'directory':'Data', 'filename':f'{name}.csv','password':'','server':''})
        rel = el(cn,'relation', name=f'{name}#csv', table=f'[{name}#csv]', type='table')
        cols = el(rel, 'columns', character_set='UTF-8', header='yes', locale='en_US', separator=',', text_qualifier='"')
        for i, field in enumerate(rows[0]):
            vals = [r[field] for r in rows if r[field]!='']
            numeric = bool(vals) and all(re.fullmatch(r'-?\d+(\.\d+)?', x) for x in vals)
            dtype = ('real' if any('.' in x for x in vals) else 'integer') if numeric else 'date' if vals and all(re.fullmatch(r'\d{4}-\d{2}-\d{2}', x) for x in vals) else 'string'
            role = 'measure' if numeric else 'dimension'
            fields[field] = {'datatype':dtype,'name':f'[{field}]','caption':field.replace('_',' ').title(), 'role':role,'type':'quantitative' if numeric else 'ordinal' if dtype=='date' else 'nominal'}
            el(cols,'column',datatype=dtype,name=field,ordinal=i)
        el(ds,'aliases',enabled='yes')
        for field, attrs in fields.items():
            col = el(ds,'column',**attrs)
            if attrs['role']=='measure':
                col.set('default-format','p0.0%' if 'rate' in field or 'share' in field else 'n#,##0.00' if 'value' in field or 'aov' in field else 'n#,##0')
        definitions[name] = fields
    worksheets = el(workbook,'worksheets')
    sheet_names = []

    def sheet(title, source, measure, dimension=None, mark='Bar', color='#167d8d', percent=False):
        sheet_names.append(title)
        ds = f'textscan.{source}'
        full = lambda instance: f'[{ds}].{instance}'
        mi = f'[sum:{measure}:qk]'
        continuous_date = dimension and definitions[source][dimension]['datatype']=='date'
        di = f'[none:{dimension}:qk]' if continuous_date else f'[none:{dimension}:nk]' if dimension else None
        ws = el(worksheets,'worksheet',name=title)
        ft = el(el(el(ws,'layout-options'),'title'),'formatted-text')
        el(ft,'run',title,bold='true',fontcolor='#122d3f',fontsize='12')
        table = el(ws,'table')
        view = el(table,'view')
        el(el(view,'datasources'),'datasource',caption=source.replace('_',' ').title(),name=ds)
        deps = el(view,'datasource-dependencies',datasource=ds)
        for field in [measure]+([dimension] if dimension else []):
            el(deps,'column',**definitions[source][field])
        el(deps,'column-instance',column=f'[{measure}]',derivation='Sum',name=mi,pivot='key',type='quantitative')
        if dimension:
            el(deps,'column-instance',column=f'[{dimension}]',derivation='None',name=di,pivot='key',type='quantitative' if continuous_date else 'nominal')
        el(view,'aggregation',value='true')
        style = el(table,'style')
        sr = el(style,'style-rule',element='cell')
        el(sr,'format',attr='text-format',field=full(mi),value='p0.0%' if percent else 'n#,##0.00' if 'value' in measure else 'n#,##0')
        sr = el(style,'style-rule',element='worksheet')
        el(sr,'format',attr='font-family',value='Arial')
        el(sr,'format',attr='display-field-labels',scope='cols',value='false')
        el(sr,'format',attr='display-field-labels',scope='rows',value='false')
        pane = el(el(table,'panes'),'pane',selection_relaxation_option='selection-relaxation-allow')
        el(el(pane,'view'),'breakdown',value='auto')
        el(pane,'mark',**{'class':mark if dimension else 'Text'})
        enc = el(pane,'encodings')
        if not dimension or mark=='Bar':
            el(enc,'text',column=full(mi))
        sr = el(el(pane,'style'),'style-rule',element='mark')
        el(sr,'format',attr='mark-color',value=color)
        el(sr,'format',attr='mark-labels-show',value='false' if mark=='Line' else 'true')
        el(sr,'format',attr='font-size',value='25' if not dimension else '10')
        el(table,'rows',full(mi) if dimension and mark=='Line' else full(di) if dimension else '')
        el(table,'cols',full(di) if dimension and mark=='Line' else full(mi) if dimension else '')

    sheet('Gross value (CU)','overview','gross_value')
    sheet('Retained value (CU)','overview','retained_value')
    sheet('Returned value (CU)','overview','returned_value',color='#cd5b45')
    sheet('Order return rate','overview','order_return_rate',percent=True,color='#cd5b45')
    sheet('Monthly retained value','monthly','retained_value','month','Line')
    sheet('Returned value by category','category','returned_value','category',color='#cd5b45')
    sheet('Region order return rate','region','order_return_rate','region',percent=True,color='#cd5b45')
    sheet('Category value return rate','category','value_return_rate','category',percent=True,color='#cd5b45')
    sheet('Purchasing customers','retention_summary','purchasing_customers')
    sheet('90-day repeat rate','retention_summary','repeat_rate_90d',percent=True)
    sheet('Eligible customers','retention_summary','eligible_customers_90d')
    sheet('Win-back review','retention_summary','winback_review_customers')
    sheet('Customers by recency','segments','customers','activity_segment')
    sheet('Retained value by recency','segments','retained_value','activity_segment')
    sheet('90-day repeat by cohort','repeat_90d','repeat_rate_90d','acquisition_quarter',percent=True)
    sheet('Monthly orders','monthly','orders','month','Line')

    dashboards = el(workbook,'dashboards')
    dashboard_names = ['01 Sales and Returns', '02 Customer Retention']
    for index, name in enumerate(dashboard_names):
        dash = el(dashboards,'dashboard',name=name)
        ft = el(el(el(dash,'layout-options'),'title'),'formatted-text')
        title_text = ('SALES & RETURNS | Recorded lines (CU); 147 orders lack amounts | Boundary months partial'
                      if index==0 else 'CUSTOMER RETENTION | As of 14 Apr 2025 | Complete 90-day follow-up only')
        el(ft,'run',title_text,bold='true',fontcolor='#ffffff',fontsize='14')
        el(dash,'style')
        el(dash,'size',maxheight='700',maxwidth='1100',minheight='700',minwidth='1100',sizing_mode='fixed')
        zones = el(dash,'zones')
        title = el(zones,'zone',h='11500',id='1',type_v2='title',w='100000',x='0',y='0')
        zs = el(title,'zone-style');el(zs,'format',attr='background-color',value='#122d3f');el(zs,'format',attr='padding',value='16')
        chosen = sheet_names[index*8:(index+1)*8]
        positions = [(1500+i*24500,13500,23000,12500) for i in range(4)]+[(1500,28500,58000,33000),(61500,28500,37000,33000),(1500,64000,58000,33500),(61500,64000,37000,33500)]
        for j,(sheet_name,(x,y,w,h)) in enumerate(zip(chosen,positions),2):
            zone=el(zones,'zone',h=h,id=j,name=sheet_name,w=w,x=x,y=y)
            zs=el(zone,'zone-style')
            for attr,value in [('background-color','#ffffff'),('border-color','#dce6eb'),('border-style','solid'),('border-width','1'),('margin','4')]:
                el(zs,'format',attr=attr,value=value)
    windows=el(workbook,'windows',source_height='36')
    for name in sheet_names:
        win=el(windows,'window',**{'class':'worksheet','name':name})
        el(win,'cards')
        el(el(win,'viewpoint'),'zoom',type='entire-view')
    for name in dashboard_names:
        win=el(windows,'window',**{'class':'dashboard','name':name})
        vps=el(win,'viewpoints')
        for sheet_name in sheet_names:
            vp=el(vps,'viewpoint',name=sheet_name);el(vp,'zoom',type='entire-view')
        el(win,'active',id='-1')
        el(win,'device-preview')
    for win in reversed(list(windows)):
        if win.get('class')=='dashboard':
            windows.remove(win)
            windows.insert(0,win)
    el(workbook,'thumbnails')
    ET.indent(workbook,space='  ')
    path=folder/'Commerce.twb'
    ET.ElementTree(workbook).write(path,encoding='utf-8',xml_declaration=True)
    with zipfile.ZipFile(folder/'Commerce.twbx','w',zipfile.ZIP_DEFLATED) as archive:
        archive.write(path,path.name)
        for p in sorted((folder/'Data').glob('*.csv')):
            archive.write(p,'Data/'+p.name)

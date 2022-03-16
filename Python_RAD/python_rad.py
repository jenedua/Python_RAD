import pooler
from datetime import datetime
from datetime import date

from osv import fields, osv
from tools.translate import _
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

#global count


class gimmel_sped_ecd(osv.osv):
   # count = 0

    _reg0990 = {}
    _regI990 = {}
    _regJ990 = {}
    _reg9900 = {}
    _reg9990 = {}
    _reg9999 = {}

    def _get_endfiscalyear(self, cr, uid, context):

        data_atual = date.today()
        # raise osv.except_osv(('Error'), data_atual)
        ano = int(data_atual.year) - 1
        enc_ano_fisc = str(ano) + '-12-31'
        return enc_ano_fisc

    _name = 'gimmel.sped.ecd'

    _columns = {
        'file': fields.binary('Arquivo', readonly=True),
        'file_name': fields.char('Nome Arquivo', 40, readonly=True),
        'state': fields.selection([('init', 'init'), ('done', 'done')], 'state', readonly=True),
        'company_id': fields.many2one('res.company', 'Empresa', select=True, required=True),
        'date_from': fields.date("Data Inicial", required=True),
        'date_to': fields.date("Data Final", required=True),
        'ind_sit_esp': fields.selection([('1', 'Cisao'), ('2', 'Fusao'), ('3', 'Incorporacao'), ('4', 'Extincao')],
                                        'Indicador Situacao Special'),
        'ind_sit_ini_per': fields.selection([('0', 'Normal'), ('1', 'Abertura'), ('2', 'Resultante de cisao/fusao'),
                                             ('3', 'Inicio Obrigatoriedade ECD')], 'Indicador Situacao Inicio Periodo',
                                            required=True),
        'ind_nire': fields.selection([('0', 'Empresa nao possui registro na Junta Comercial'),
                                      ('1', 'Empresa possui registro na Junta Comercial ')],
                                     'Indicador De Existencia De NIRE', required=True),
        'ind_fin_esc': fields.selection([('0', 'Original'), ('1', 'Substituta')],
                                        'Indicador De Finalidade Da Estruturacao', required=True),
        'cod_hash_sub': fields.char('Hash da escrituracao substituida', size=256),
        'ind_grande_porte': fields.selection([('0', 'Empresa nao e entidade sujeita a auditoriaindependente'),
                                              ('1', 'Empresa e entidade sujeita a auditoria independente')],
                                             'Indicador De Entidade Sujeita a Auditoria', required=True),
        'tip_ecd': fields.selection([('0', 'ECD de empresa nao participante de SCP como socio ostensivo'),
                                     ('1', 'ECD de empresa participante de SCP como socio ostensivo'),
                                     ('2', 'ECD da SCP')], 'Indicador Do Tipo De ECD', required=True),
        'cod_scp': fields.char('Identificacao da SCP', size=256),
        'ident_mf': fields.selection([('S', 'Sim'), ('N', 'Nao')], 'Identificao moeda Funcional', required=True),
        'ind_esc_cons': fields.selection([('S', 'Sim'), ('N', 'Nao')], 'Indicador Escritura Consolidado',
                                         required=True),
        'ind_centralizada': fields.selection(
            [('0', 'Escrituracao Centralizada'), ('1', 'Escrituracao Descentralizada')], 'Indicador Centralizado',
            required=True),
        'ind_mudanc_pc': fields.selection(
            [('0', 'Nao houve mudanca no plano de contas'), ('1', 'Houve mudanca no plano de contas')],
            'Indicador Mudanca De Plano De Contas', required=True),
        'cod_plan_ref': fields.selection(
            [('1', 'PJ em Geral-Lucro Real'), ('2', 'PJ em Geral-Lucro Presumido'), ('3', 'Financeiras-Lucro Real'),
             ('4', 'Seguradoras-Lucro Real'), ('5', 'Imunes e Isentas em Geral'),
             ('6', ' Imunes e Isentas-Financeiras'), ('7', 'Imunes e Isentas-Seguradoras'),
             ('8', 'Entidades Fechadas de Previdencia Complementar'), ('9', 'Partidos Politicos'),
             ('10', 'Financeiras-Lucro Presumido')], 'Codigo Do Plano De Contas Referencial'),
        'dt_ex_social': fields.date("Data de encerramento do exercicio social", required=True)
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'dt_ex_social': _get_endfiscalyear,
        'file_name': lambda *a: 'ECD_' + datetime.now().strftime('%m%y') + '.txt',
        'state': 'init'
    }

    def _registro0000(self, cr, uid, form):
        linha = '|0000|LECD'
        data_ini1 = form['date_from']
        data_ini = datetime.strptime(data_ini1, "%Y-%m-%d")
        data_ini = str(datetime.strftime(data_ini, "%d%m%Y")) or ''
        linha += '|' + data_ini
        data_fin1 = form['date_to']
        data_fin = datetime.strptime(data_fin1, "%Y-%m-%d")
        data_fin = str(datetime.strftime(data_fin, "%d%m%Y")) or ''
        linha += '|' + data_fin
        company_obj = self.pool.get('res.company').browse(cr, uid, form['company_id'][0])
        nome = company_obj.partner_id.name
        linha += '|' + nome
        # comp_cnpj_obj = self.pool.get('res.company').browse(cr, uid, form['cnpj_cpf'][0])
        # cnpj = comp_cnpj_obj.partner_id.cnpj_cpf
        cnpj = company_obj.partner_id.cnpj_cpf
        new_cnpj = ''.join(char for char in cnpj if char.isalnum())
        linha += '|' + new_cnpj
        UF = company_obj.partner_id.address[0].state_id.code
        linha += '|' + UF
        IE = company_obj.partner_id.inscr_est
        linha += '|' + IE
        COD_MUN = company_obj.partner_id.address[0].state_id.ibge_code
        linha += '|' + COD_MUN
        IM = company_obj.partner_id.inscr_mun or ''
        linha += '|' + IM + '|'
        ind_sit_esp = form['ind_sit_esp'] or ''
        linha += str(ind_sit_esp)
        # raise osv.except_osv(('Error'), linha)
        ind_sit_ini_per = form['ind_sit_ini_per']
        linha += '|' + ind_sit_ini_per
        ind_nire = form['ind_nire'] or ''
        linha += '|' + ind_nire
        ind_fin_esc = form['ind_fin_esc'] or ''
        linha += '|' + ind_fin_esc
        cod_hash_sub = form['cod_hash_sub'] or ''
        linha += '|' + cod_hash_sub
        ind_grande_porte = form['ind_grande_porte'] or ''
        linha += '|' + ind_grande_porte
        tip_ecd = form['tip_ecd'] or ''
        linha += '|' + tip_ecd
        cod_scp = form['cod_scp'] or ''
        linha += '|' + cod_scp
        ident_mf = form['ident_mf'] or ''
        linha += '|' + ident_mf
        # raise osv.except_osv(('Error'), ident_mf)
        ind_esc_cons = form['ind_esc_cons'] or ''
        linha += '|' + ind_esc_cons
        ind_centralizada = form['ind_centralizada'] or ''
        linha += '|' + ind_centralizada
        ind_mudanc_pc = form['ind_mudanc_pc'] or ''
        linha += '|' + ind_mudanc_pc
        cod_plan_ref = form['cod_plan_ref'] or ''
        linha += '|' + cod_plan_ref + '|'
        linha += '\n'
        self._totaliza('reg0990')
        self._totaliza('reg9999')
        self._reg9900.update({'0000': self._reg9900['0000'] + 1})

        return linha

    def _registro0001(self, cr, uid, form):
        linha = '|0001|0|' + '\n'
        self._totaliza('reg0990')
        self._totaliza('reg9999')
        self._reg9900.update({'0001': self._reg9900['0001'] + 1})

        return linha

    def _registro0007(self, cr, uid, form):
        linha = '|0007|'
        company_obj = self.pool.get('res.company').browse(cr, uid, form['company_id'][0])
        UF = company_obj.partner_id.address[0].state_id.code
        linha += UF + '|' + '|' + '\n'
        self._totaliza('reg0990')
        self._totaliza('reg9999')
        self._reg9900.update({'0007': self._reg9900['0007'] + 1})

        return linha

    def _registro0990(self):
        linha = '|0990|' + str(self._reg0990['reg0990']) + '|' + '\n'           
        self._reg9900.update({'0990': self._reg9900['0990'] + 1})
        self._totaliza('reg9999')
        return linha

    def _registroI001(self, cr, uid, form):
        linha = '|I001|' 
        if {'I001': self._reg9900['I001'] + 1} > 0:
            linha += '0|' + '\n'
        else:
            linha += '1|' + '\n'
        self._totaliza('regI990')
        self._totaliza('reg9999')
        self._reg9900.update({'I001': self._reg9900['I001'] + 1})
        #raise osv.except_osv(('Error'), self._reg9900['I001'])

        return linha

    def _registroI010(self, cr, uid, form):
        linha = '|I010|G|9.00|' + '\n'
        self._totaliza('regI990')
        self._totaliza('reg9999')
        self._reg9900.update({'I010': self._reg9900['I010'] + 1})

        return linha

    def _registroI030(self, cr, uid, form):
        company_obj = self.pool.get('res.company').browse(cr, uid, form['company_id'][0])
        linha = '|I030|TERMO DE ABERTURA'
        num_ord_livro_diario = company_obj.num_ord_livro_diario
        linha += '|' + num_ord_livro_diario + '|REGISTRO DO LIVRO DIARIO' + '|Qtd tot do liv do arq'
        nome = company_obj.partner_id.name
        linha += '|' + nome
        nire = company_obj.nire
        linha += '|' + nire
        cnpj = company_obj.partner_id.cnpj_cpf
        new_cnpj = ''.join(char for char in cnpj if char.isalnum())
        linha += '|' + new_cnpj
        dt_arq1 = company_obj.dt_arq
        dt_arq2 = datetime.strptime(dt_arq1, "%Y-%m-%d")
        dt_arq = str(datetime.strftime(dt_arq2, "%d%m%Y"))
        linha += '|' + dt_arq + '|'
        desc_mun = company_obj.partner_id.address[0].l10n_br_city_id.name.upper()
        linha += '|' + desc_mun
        dt_ex_social1 = form['dt_ex_social']
        dt_ex_social2 = datetime.strptime(dt_ex_social1, "%Y-%m-%d")
        dt_ex_social = str(datetime.strftime(dt_ex_social2, "%d%m%Y"))
        linha += '|' + dt_ex_social + '|' + '\n'
        self._totaliza('regI990')
        self._totaliza('reg9999')
        self._reg9900.update({'I030': self._reg9900['I030'] + 1})

        return linha

    def _registroI050(self, cr, uid, form):
        linhas = ''
        account_obj = self.pool.get('account.account')
        account_ids = account_obj.search(cr, uid, [('code', '!=', '0')])
        if account_ids:
            for acc in account_obj.read(cr, uid, account_ids, ['code', 'name', 'parent_id', 'type']):
                linha = '|I050'
                data_ini1 = form['date_from']
                data_ini = datetime.strptime(data_ini1, "%Y-%m-%d")
                data_ini = str(datetime.strftime(data_ini, "%d%m%Y")) or ''
                linha += '|' + data_ini + '|'
                if acc['code'].count('.') + 1 == 1:
                    linha += '01|'
                if acc['code'].count('.') + 1 == 2:
                    linha += '02|'
                if acc['code'].count('.') + 1 == 3:
                    linha += '03|'
                if acc['code'].count('.') + 1 == 4:
                    linha += '04|'
                if acc['code'].count('.') + 1 == 5:
                    linha += '05|'
                linha += 'S' if acc['type'] == 'view' else 'A'
                linha += '|' + str(acc['code'].count('.') + 1)
                linha += '|' + acc['code'] + '|'  
                if acc['parent_id']:
                    parent_id = self.pool.get('account.account').browse(cr, uid, acc['parent_id'][0])
                    if parent_id.code != '0':
                        linha +=  parent_id.code + '|'                       
                    else:
                        linha += '|'                        
                else:
                    linha += '|'
                linha +=  acc['name'].upper() + '|'                
                linhas += linha + '\n'
                self._totaliza('reg9999')
                self._totaliza('regI990')
                self._reg9900.update({'I050': self._reg9900['I050'] + 1})
                
        return linhas

    def _registroI075(self, cr, uid, form):
        linha = '|I075|' + '|' + '\n'
        self._totaliza('regI990')
        self._totaliza('reg9999')
        self._reg9900.update({'I075': self._reg9900['I075'] + 1})
        return linha

    def _registroI150(self, cr, uid, form):
        linhas = ''
        data_ini1 = form['date_from']
        data_ini = datetime.strptime(data_ini1, "%Y-%m-%d")
        data_ini = str(datetime.strftime(data_ini, "%Y"))
        fy_obj = self.pool.get('account.fiscalyear')
        fy_ids = fy_obj.search(cr, uid, [('name', '=', data_ini)])
        period_obj = self.pool.get('account.period')
        p_ids = period_obj.search(cr, uid, [('fiscalyear_id', '=', fy_ids[0]), ('special', '=', False)])
        if p_ids:
            for per in period_obj.read(cr, uid, p_ids, ['date_start', 'date_stop', 'id']):
                linha = '|I150|'
                date_start1 = per['date_start']
                date_start2 = datetime.strptime(date_start1, "%Y-%m-%d")
                date_start = str(datetime.strftime(date_start2, "%d%m%Y"))
                date_stop1 = per['date_stop']
                date_stop2 = datetime.strptime(date_stop1, "%Y-%m-%d")
                date_stop = str(datetime.strftime(date_stop2, "%d%m%Y"))
                linha += date_start + '|' + date_stop + '|'                
                linha += '\n'   
                self._totaliza('regI990')
                self._totaliza('reg9999')          
                self._reg9900.update({'I150': self._reg9900['I150'] + 1})
                account_obj = self.pool.get('account.account')
                # list_obj_ids = self.pool.get('account.acount.list')
                account_ids = account_obj.search(cr, uid, [('code', '!=', '0')])
                # raise osv.except_osv(('Error'), account_ids)
                ctx = {}
                ctx['periods'] = [per['id']]
                if account_ids:
                    for acc in account_obj.read(cr, uid, account_ids, ['code', 'name', 'parent_id', 'type', 'balance', 'debit', 'credit'], ctx):
                        #raise osv.except_osv(('Error'), acc['code'])
                        type = acc['code'][0:1]
                        if type == '1' or type == '3':
                            inicial = round(acc['balance'], 2) - round(acc['debit'], 2) + round(acc['credit'], 2)
                            if inicial != 0 or acc['debit'] != 0 or acc['credit'] != 0 or acc['balance'] != 0:
                                linha += '|I155'
                                linha += '|' + acc['code'] + '|' + '|'                               
                                if acc['balance'] >= 0:
                                    linha += 'D' + '|'                                    
                                else:
                                    linha += 'C' + '|'                                    
                                if inicial < 0:
                                    inicial = inicial * -1
                                if acc['balance'] < 0:
                                    acc['balance'] = acc['balance'] * -1
                                linha += str(round(inicial, 2)) + '|'
                                linha += str(acc['debit']) + '|'
                                linha += str(acc['credit']) + '|'
                                linha += str(acc['balance']) + '|'                                
                                if acc['balance'] >= 0:
                                    linha += 'D' + '|'                                   
                                else:
                                    linha += 'C' + '|' 
                                linha += '\n' 
                                self._totaliza('regI990')                                    
                                self._reg9900.update({'I155': self._reg9900['I155'] + 1})
                                self._totaliza('reg9999')                             
                        elif type == '2' or type == '4':
                            inicial = round(acc['balance'], 2) + round(acc['debit'], 2) - round(acc['credit'], 2)
                            if inicial != 0 or acc['debit'] != 0 or acc['credit'] != 0 or acc['balance'] != 0:
                                linha += '|I155'
                                linha += '|' + acc['code'] + '|' + '|'                              
                                if acc['balance'] >= 0:
                                    linha += 'C' + '|'                                    
                                else:
                                    linha += 'D' + '|'                                    
                                if inicial < 0:
                                    inicial = inicial * -1
                                if acc['balance'] < 0:
                                    acc['balance'] = acc['balance'] * -1
                                linha += str(round(inicial, 2)) + '|'
                                linha += str(acc['debit']) + '|'
                                linha += str(acc['credit']) + '|'
                                linha += str(acc['balance']) + '|'
                                if acc['balance'] >= 0:
                                    linha += 'C' + '|'                                     
                                else:
                                    linha += 'D' + '|'
                                linha += '\n'                              
                                self._totaliza('regI990')                                    
                                self._reg9900.update({'I155': self._reg9900['I155'] + 1})
                                self._totaliza('reg9999')

                linhas += linha

        return linhas

    def _registroI200(self, cr, uid, form):
        linhas = ''
        data_ini1 = form['date_from']
        data_ini = datetime.strptime(data_ini1, "%Y-%m-%d")
        data_ini = str(datetime.strftime(data_ini, "%Y"))
        fy_obj = self.pool.get('account.fiscalyear')
        fy_ids = fy_obj.search(cr, uid, [('name', '=', data_ini)])
        period_obj = self.pool.get('account.period')
        # raise osv.except_osv(('Error'), fy_obj)
        p_ids = period_obj.search(cr, uid, [('fiscalyear_id', '=', fy_ids[0]), ('special', '=', False)])
        if p_ids:
            for per in period_obj.read(cr, uid, p_ids, ['date_start', 'date_stop', 'id']):
                linha = '|I200|' + '|'
                date_start1 = per['date_start']
                date_start2 = datetime.strptime(date_start1, "%Y-%m-%d")
                date_start = str(datetime.strftime(date_start2, "%d%m%Y"))
                linha += date_start + '|'                                                                 
                linha += '\n'
                self._totaliza('regI990')
                self._totaliza('reg9999')
                self._reg9900.update({'I200': self._reg9900['I200'] + 1})
                account_obj = self.pool.get('account.account')
                account_ids = account_obj.search(cr, uid, [('code', '!=', '0')])
                if account_ids:
                    for acc in account_obj.read(cr, uid, account_ids, ['code', 'name', 'parent_id', 'type', 'balance', 'debit', 'credit']):
                        type = acc['code'][0:1]
                        if type == '1' or type == '3':
                            if acc['debit'] > 0:
                                linha += '|I250|'
                                linha += acc['code'] + '|' + '|'
                                linha += str(acc['debit']) + '|'
                                if acc['balance'] > 0:
                                    linha += 'D' + '|' + '|'                                   
                                else:
                                    linha += 'C' + '|' + '|'
                                linha += '817|'
                                linha += acc['name'] +'|' + '|'
                                linha += '\n'
                                self._totaliza('regI990')
                                self._totaliza('reg9999')                          
                                self._reg9900.update({'I250': self._reg9900['I250'] + 1}) 
                                
                        elif type == '2' or type == '4':
                            if acc['debit'] > 0:
                                linha += '|I250|'
                                linha += acc['code'] + '|' + '|'                                                           
                                linha += str(acc['debit']) + '|'
                                if acc['balance'] > 0:
                                    linha += 'D' + '|' + '|'                                  
                                else:
                                    linha += 'C' + '|' + '|'
                                linha += '817|'
                                linha += acc['name'] +'|' +'|'
                                linha += '\n'
                                self._totaliza('regI990')
                                self._totaliza('reg9999')                          
                                self._reg9900.update({'I250': self._reg9900['I250'] + 1})
                            
                    linhas += linha

        return linhas
    
    def _registroI350(self, cr, uid, form):
        linhas = ''
        linha = '|I350|'
        data_atual = date.today()
        # raise osv.except_osv(('Error'), data_atual)
        ano = int(data_atual.year) - 1
        enc_ano_fisc = '3112' + str(ano) + '|'
        linha += enc_ano_fisc
        self._totaliza('regI990')
        self._totaliza('reg9999')
        self._reg9900.update({'I350': self._reg9900['I350'] + 1})
        linha += '\n'
        # linhas += linha
        data_ini1 = form['date_to']
        data_ini = datetime.strptime(data_ini1, "%Y-%m-%d")
        data_ini = str(datetime.strftime(data_ini, "%Y"))
        fy_obj = self.pool.get('account.fiscalyear')
        fy_ids = fy_obj.search(cr, uid, [('name', '=', data_ini)])
        period_obj = self.pool.get('account.period')
        p_ids = period_obj.search(cr, uid, [('fiscalyear_id', '=', fy_ids[0]), ('special', '=', False)])
        if p_ids:            
            account_obj = self.pool.get('account.account')
            account_ids = account_obj.search(cr, uid, [('code', '!=', '0')])                
            if account_ids:
                for acc in account_obj.read(cr, uid, account_ids, ['code', 'name', 'parent_id', 'type', 'balance', 'debit', 'credit']):
                    type = acc['code'][0:1]
                    if type == '3' or type == '4':
                        if acc['balance'] != 0:
                            linha += '|I355|'
                            linha += acc['code'] + '|' + '|'
                            if acc['balance'] < 0:
                                acc['balance'] = acc['balance'] * -1
                            linha += str(acc['balance']) + '|'                                
                            if acc['balance'] >= 0:
                                linha += 'D' + '|'                                    
                            else:
                                linha += 'C' + '|' 
                            linha += '\n'                                                            
                            self._totaliza('regI990')
                            self._totaliza('reg9999')
                            self._reg9900.update({'I355': self._reg9900['I355'] + 1})                    
                linhas += linha

        return linhas
    
    def _registroI990(self):
        linha = '|I990|' + str(self._regI990['regI990']) + '|' + '\n'
        self._totaliza('reg9999')
        self._reg9900.update({'I990': self._reg9900['I990'] + 1})
        return linha

    def _registroJ001(self, cr, uid, form):
        linha = '|J001|'
        if {'J001': self._reg9900['J001'] + 1}:
            linha += '0|' + '\n'
        else:
            linha += '1|' + '\n'
        self._totaliza('regJ990')
        self._totaliza('reg9999')
        self._reg9900.update({'J001': self._reg9900['J001'] + 1})
        return linha

    def _registroJ005(self, cr, uid, form):
        linha = '|J005'
        data_ini1 = form['date_from']
        data_ini = datetime.strptime(data_ini1, "%Y-%m-%d")
        data_ini = str(datetime.strftime(data_ini, "%d%m%Y")) or ''
        linha += '|' + data_ini
        data_fin1 = form['date_to']
        data_fin = datetime.strptime(data_fin1, "%Y-%m-%d")
        data_fin = str(datetime.strftime(data_fin, "%d%m%Y")) or ''
        linha += '|' + data_fin + '|1||' + '\n'
        self._totaliza('regJ990')
        self._totaliza('reg9999')
        self._reg9900.update({'J005': self._reg9900['J005'] + 1})
        return linha

    def _registroJ100(self, cr, uid, form):
        linha = '|J100|' + '\n'
        self._totaliza('regJ990')
        self._totaliza('reg9999')
        self._reg9900.update({'J100': self._reg9900['J100'] + 1})
        return linha

    def _registroJ150(self, cr, uid, form):
        linha = '|J150|' + '\n'
        self._totaliza('regJ990')
        self._totaliza('reg9999')
        self._reg9900.update({'J150': self._reg9900['J150'] + 1})
        return linha

    def _registroJ900(self, cr, uid, form):
        linha = '|J900|TERMO DE ENCERRAMENTO'
        company_obj = self.pool.get('res.company').browse(cr, uid, form['company_id'][0])
        num_ord_livro_diario = company_obj.num_ord_livro_diario
        linha += '|' + num_ord_livro_diario + '|REGISTRO DO LIVRO DIARIO'
        nome = company_obj.partner_id.name
        linha += '|' + nome
        data_ini1 = form['date_from']
        data_ini = datetime.strptime(data_ini1, "%Y-%m-%d")
        data_ini = str(datetime.strftime(data_ini, "%d%m%Y")) or ''
        linha += '|' + data_ini
        data_fin1 = form['date_to']
        data_fin = datetime.strptime(data_fin1, "%Y-%m-%d")
        data_fin = str(datetime.strftime(data_fin, "%d%m%Y")) or ''
        linha += '|' + data_fin + '|' + '\n'
        self._totaliza('regJ990')
        self._totaliza('reg9999')
        self._reg9900.update({'J900': self._reg9900['J900'] + 1})
        return linha

    def _registroJ930(self, cr, uid, form):
        linha = '|J930|MARCIA M C GOMES|' + '\n'
        linha += '|J930|'
        company_obj = self.pool.get('res.company').browse(cr, uid, form['company_id'][0])
        nome = company_obj.partner_id.name
        linha += nome + '|' + '\n'
        self._reg9900.update({'J930': self._reg9900['J930'] + 1})
        self._totaliza('regJ990')
        self._totaliza('reg9999')
        return linha

    def _registroJ990(self):
        linha = '|J990|' + str(self._regJ990['regJ990']) + '|' + '\n'
        self._reg9900.update({'J990': self._reg9900['J990'] + 1})  
        self._totaliza('reg9999')
             
        return linha
    
    def _registro9001(self, cr, uid, form):
        linha = '|9001|' 
        if {'9001': self._reg9900['9001'] + 1} > 0:
            linha += '0|' + '\n'
        else:
            linha += '1|' + '\n'
            
        self._totaliza('reg9999')
        self._reg9900.update({'9001': self._reg9900['9001'] + 1})
        
        return linha 

    
    
    
    def _registro9999(self):
        linha = '|9999|' + str(self._reg9999['reg9999']) + '|' + '\n'
        self._totaliza('reg9999')
               
        
        return linha 

    
    def _registro9990(self):
        linha = '|9900|9990|' + str(self._reg9990['reg9990']) + '|' + '\n' 
        self._totaliza('reg9999') 
              
        return linha 
    
    def _registro999f(self):
        linha = '|9900|9999|' + str(self._reg999f['reg999f']) + '|' + '\n'
        self._totaliza('reg9999') 
        
        return linha      

    def _totaliza(self, reg):
        
        if reg == 'reg0990':
            self._reg0990.update({'reg0990': self._reg0990['reg0990'] + 1})
            
        if reg == 'regI990':
            self._regI990.update({'regI990': self._regI990['regI990'] + 1})

        if reg == 'regJ990':
            self._regJ990.update({'regJ990': self._regJ990['regJ990'] + 1})

        if reg == 'reg9900':
            self._reg9900.update({'reg9900': self._reg9900['reg9900'] + 1})

        if reg == 'reg9990':
            self._reg9990.update({'reg9990': self._reg9990['reg9990'] + 1})
            
        if reg == 'reg999f':        
            self._reg999f.update({'reg999f': self._reg999f['reg999f'] + 1})

        if reg == 'reg9999':
            self._reg9999.update({'reg9999': self._reg9999['reg9999'] + 1})

        return

    def check_report(self, cr, uid, ids, context=None):

        self._reg0990 = {'reg0990': 1}
        self._regI990 = {'regI990': 1}
        self._regJ990 = {'regJ990': 1}
        self._reg9990 = {'reg9990': 1}
        self._reg999f = {'reg999f': 1}
        self._reg9999 = {'reg9999': 1}        
        self._reg9900 = {
            '0000': 0,
            '0001': 0,
            '0007': 0,
            '0990': 0,
            'I001': 0,
            'I010': 0,
            'I030': 0,
            'I050': 0,
            'I051': 0,
            'I052': 0,
            'I053': 0,
            'I075': 0,
            'I150': 0,
            'I155': 0,
            'I200': 0,
            'I250': 0,
            'I300': 0,
            'I310': 0,
            'I350': 0,
            'I355': 0,
            'I990': 0,
            'J001': 0,
            'J005': 0,
            'J100': 0,
            'J150': 0,
            'J210': 0,
            'J215': 0,
            'J900': 0,
            'J930': 0,
            'J932': 0,
            'J935': 0,
            'J990': 0,
            '9001': 0

        }
       

        form = self.read(cr, uid, ids,
                         ['company_id', 'date_from', 'date_to', 'ind_sit_esp', 'ind_sit_ini_per', 'ind_nire',
                          'cod_hash_sub', 'ind_fin_esc', 'ind_grande_porte',
                          'tip_ecd', 'cod_scp', 'ident_mf', 'ind_esc_cons', 'ind_centralizada', 'ind_mudanc_pc',
                          'cod_plan_ref', 'dt_ex_social'], context=context)[0]

        fbuffer = StringIO()
        if context is None:
            context = {}

        fbuffer.write(unicode(self._registro0000(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registro0001(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registro0007(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registro0990()).encode('utf8'))        
        fbuffer.write(unicode(self._registroI001(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroI010(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroI030(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroI050(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroI075(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroI150(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroI200(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroI350(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroI990()).encode('utf8'))
        fbuffer.write(unicode(self._registroJ001(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroJ005(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroJ100(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroJ150(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroJ900(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroJ930(cr, uid, form)).encode('utf8'))
        fbuffer.write(unicode(self._registroJ990()).encode('utf8'))
        fbuffer.write(unicode(self._registro9001(cr, uid, form)).encode('utf8'))
        
        k1 = 0
        for k in  sorted(self._reg9900.keys()):
            k1 +=1
            linha = '|9900|' + str(k) + '|' + str(self._reg9900[k]) + '|' + '\n'
            self._totaliza('reg9999')    
            fbuffer.write(unicode(linha).encode('utf8'))
            
        linha = '|9900|' + '9900|' + str(k1) + '|' + '\n'            
        fbuffer.write(unicode(linha).encode('utf8'))
        
        fbuffer.write(unicode(self._registro9990()).encode('utf8'))
        fbuffer.write(unicode(self._registro999f()).encode('utf8'))
        
        counter = 0
        for r in (self._reg9990 , self._reg9900, self._reg9999):
            counter += 1  
            self._totaliza('reg9999')                  
        linha = '|9990|' + str(k1 + counter)+ '|' + '\n' 
        
        fbuffer.write(unicode(linha).encode('utf8'))
        
        fbuffer.write(unicode(self._registro9999()).encode('utf8'))   
       
        _file = fbuffer.getvalue().encode("base64")

        self.write(cr, uid, ids, {'file': _file, 'state': 'done'}, context=context)


gimmel_sped_ecd()
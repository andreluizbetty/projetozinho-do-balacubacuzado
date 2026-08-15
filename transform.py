import validate


class Transform:
    #Todo impremente isto no validate, e não no transform, cujo proposito é TRASNFORMAR
    def __init__(self, data):
        vd = validate.Validator()
        result_validate = vd.validate_dict_xml(data)


    @staticmethod
    def transform_nfe(xml):
        inf = xml["nfeProc"]["NFe"]["infNFe"]
        prot = xml["nfeProc"]["protNFe"]["infProt"]

        return {
            "numero": inf["ide"]["nNF"],
            "serie": inf["ide"]["serie"],
            "chave": prot["chNFe"],
            "data_emissao": inf["ide"]["dhEmi"],
            "tipo": int(inf["ide"]["tpNF"]),

            "cnpj_emitente": inf["emit"]["CNPJ"],
            "razao_social_emitente": inf["emit"]["xNome"],

            "cnpj_destinatario": inf["dest"]["CNPJ"],
            "razao_social_destinatario": inf["dest"]["xNome"],

            "valor_total": inf["total"]["ICMSTot"]["vNF"],

            "protocolo": prot["nProt"],
            "status": int(prot["cStat"]),
            "descricao_status": prot["xMotivo"]}
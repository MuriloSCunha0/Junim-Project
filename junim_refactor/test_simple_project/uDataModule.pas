unit uDataModule;

interface

uses
  System.SysUtils, System.Classes, FireDAC.Stan.Intf, FireDAC.Stan.Option,
  FireDAC.Stan.Error, FireDAC.UI.Intf, FireDAC.Phys.Intf, FireDAC.Stan.Def,
  FireDAC.Stan.Pool, FireDAC.Stan.Async, FireDAC.Phys, FireDAC.Phys.SQLite,
  FireDAC.Phys.SQLiteDef, FireDAC.Stan.ExprFuncs, FireDAC.VCLUI.Wait,
  Data.DB, FireDAC.Comp.Client, FireDAC.Stan.Param, FireDAC.DatS,
  FireDAC.DApt.Intf, FireDAC.DApt, FireDAC.Comp.DataSet;

type
  TDataModule1 = class(TDataModule)
    Connection: TFDConnection;
    QryClientes: TFDQuery;
    QryClientesID: TFDAutoIncField;
    QryClientesNome: TStringField;
    QryClientesEmail: TStringField;
    QryClientesTelefone: TStringField;
    QryClientesDataCadastro: TDateField;
    QryProdutos: TFDQuery;
    QryProdutosID: TFDAutoIncField;
    QryProdutosNome: TStringField;
    QryProdutosDescricao: TStringField;
    QryProdutosPreco: TSingleField;
    QryProdutosEstoque: TIntegerField;
    QryProdutosAtivo: TBooleanField;
    QryVendas: TFDQuery;
    QryVendasID: TFDAutoIncField;
    QryVendasClienteID: TIntegerField;
    QryVendasProdutoID: TIntegerField;
    QryVendasQuantidade: TIntegerField;
    QryVendasValorTotal: TSingleField;
    QryVendasDataVenda: TDateField;
    procedure DataModuleCreate(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    procedure CriarTabelas;
  end;

var
  DataModule1: TDataModule1;

implementation

{%CLASSGROUP 'Vcl.Controls.TControl'}

{$R *.dfm}

procedure TDataModule1.DataModuleCreate(Sender: TObject);
begin
  // Configurar conexão SQLite
  Connection.Params.Database := 'simple_crud.db';
  Connection.Connected := True;
  CriarTabelas;
end;

procedure TDataModule1.CriarTabelas;
begin
  // Criar tabela de clientes
  Connection.ExecSQL(
    'CREATE TABLE IF NOT EXISTS Clientes (' +
    'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
    'Nome VARCHAR(100) NOT NULL, ' +
    'Email VARCHAR(100), ' +
    'Telefone VARCHAR(20), ' +
    'DataCadastro DATE' +
    ')'
  );
  
  // Criar tabela de produtos
  Connection.ExecSQL(
    'CREATE TABLE IF NOT EXISTS Produtos (' +
    'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
    'Nome VARCHAR(100) NOT NULL, ' +
    'Descricao TEXT, ' +
    'Preco REAL, ' +
    'Estoque INTEGER, ' +
    'Ativo BOOLEAN DEFAULT 1' +
    ')'
  );
  
  // Criar tabela de vendas
  Connection.ExecSQL(
    'CREATE TABLE IF NOT EXISTS Vendas (' +
    'ID INTEGER PRIMARY KEY AUTOINCREMENT, ' +
    'ClienteID INTEGER, ' +
    'ProdutoID INTEGER, ' +
    'Quantidade INTEGER, ' +
    'ValorTotal REAL, ' +
    'DataVenda DATE, ' +
    'FOREIGN KEY (ClienteID) REFERENCES Clientes(ID), ' +
    'FOREIGN KEY (ProdutoID) REFERENCES Produtos(ID)' +
    ')'
  );
end;

end.
